import datetime as dt
import os
import sqlite3
import time
from contextlib import suppress

from config_module import myconfig


# noinspection PyUnusedLocal
class CacheDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db_conn = sqlite3.connect(str(db_path))
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS cache_table(
                key      TEXT     PRIMARY KEY,
                value          TEXT,
                store_dt datetime
            );
        ''')

    def query(self, key, start_date_time=None):
        if start_date_time is None:
            exec_str = f"select * from cache_table where key == '{key}'"
        else:
            exec_str = f"select * from cache_table where key == '{key}' " \
                       f"and store_dt >= '{str(start_date_time)}'"
        print(exec_str)
        cursor = self.db_conn.execute(exec_str)
        rows = [val for val in cursor]
        if len(rows) == 1:
            return rows[0][1]
        return None

    def query_many(self, keys, start_date_time=None):
        if start_date_time is None:
            time_filter_str = ''
        else:
            time_filter_str = f' and store_dt >= "{str(start_date_time)}"'

        keys_str = ','.join(["'" + key + "'" for key in keys])

        query_str = f'select * from cache_table where key in({keys_str})' + time_filter_str
        cursor = self.db_conn.execute(query_str)
        result_dict = {}
        for row in cursor:
            result_dict[row[0]] = row[1]
        return result_dict

    def update(self, key, value):
        time_str = str(dt.datetime.now())
        print('time_str', time_str)
        execute_str = f"INSERT OR REPLACE into cache_table values " \
                      f"('{key}','{value}','{time_str}');"
        print(execute_str)
        val = self.db_conn.execute(execute_str)
        self.db_conn.commit()

    def close(self):
        self.db_conn.close()


cache_db = CacheDatabase(myconfig.project_root / 'cache.db')


def test_cache_database():
    path = myconfig.project_root / 'test_cache_db.db'
    with suppress(FileNotFoundError):
        os.remove(path)
    db = CacheDatabase(path)
    dt0 = dt.datetime.now()
    time.sleep(0.1)
    db.update('k1', 'v1')
    time.sleep(0.1)
    dt1 = dt.datetime.now()
    time.sleep(0.1)
    db.update('k2', 'v2')
    time.sleep(0.1)
    dt2 = dt.datetime.now()

    val = db.query('k1')
    assert val == 'v1'

    val = db.query('k1', dt0)
    assert val == 'v1'
    val = db.query('k1', dt1)
    assert not val

    val = db.query_many(['k1', 'k2'])
    assert set(val) == set(['k1', 'k2'])

    val = db.query_many(['k1', 'k2'], start_date_time=dt1)
    assert set(val) == set(['k2'])

    val = db.query_many(['k1', 'k2'], start_date_time=dt2)
    assert not len(val)

    db.close()
    with suppress(FileNotFoundError):
        os.remove(path)


def main():
    test_cache_database()


if __name__ == '__main__':
    main()