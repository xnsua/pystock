import json
import os
from pathlib import Path

from common.helper import save_string_to_file, read_string_from_file


class Config:
    kdata_path = 'pydata'
    kfund_path = 'fund'
    kstock_path = 'stock'
    config_filename = 'config.json'

    def __init__(self):
        if os.path.exists(self.config_filename):
            jstr = read_string_from_file(self.config_filename)
            self.config_json = json.loads(jstr)
        else:
            self.config_json = {}

    def __getitem__(self, item):
        return self.config_json[item]

    def __setitem__(self, key, value):
        self.config_json[key] = value
        self.save()

    def get_config_path(self):
        p = Path('..') / self.config_filename
        return str(p)

    def save(self):
        jstr = json.dumps(self.config_json, ensure_ascii=False)
        save_string_to_file(jstr, self.get_config_path())

    def get_fund_data_path(self):
        path = self.get_project_root().parent / self.kdata_path / self.kfund_path
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @staticmethod
    def get_project_root():
        p = Path('..').resolve()
        assert p.name == 'PyStock'
        return Path(p)


config = Config()

if __name__ == '__main__':
    print(config.get_fund_data_path())
    config.get_project_root()
    pass