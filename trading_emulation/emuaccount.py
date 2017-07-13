import copy
from typing import List, Dict

from nose.tools import assert_equal

from ip.st import EntrustWay
from stock_data_updater.data_provider import gdp
from trading.abstract_account import AbstractAccount


def set_account_none_fee():
    EmuAccount.buy_fee = 0
    EmuAccount.buy_fee_tuple = (0, 10000)
    EmuAccount.sell_fee = 0
    EmuAccount.tax = 0


def set_account_fee():
    EmuAccount.buy_fee = 25 / 100_000
    EmuAccount.buy_fee_tuple = (25, 100_000)
    EmuAccount.sell_fee = 25 / 100_000
    EmuAccount.tax = 1 / 1_000


class EmuShare:
    def __init__(self, stock_code, price, amount, time, cost_money):
        self.stock_code = stock_code
        self.amount = amount
        self.price = price
        self.time = time
        self.cost_money = cost_money

    def __repr__(self):
        return f'Share{{code:{self.stock_code}, amount:{self.amount}}}'


class WinInfo:
    def __init__(self, stock_code, buy_day, sell_day, win_percentage):
        self.buy_day = buy_day
        self.sell_day = sell_day
        self.win_percentage = win_percentage
        self.stock_code = stock_code


class EmuAccount(AbstractAccount):
    @property
    def entrust_items(self):
        return None

    @property
    def share_items(self):
        return None

    def cancel_order(self, enetrust_id, code, way: EntrustWay):
        pass

    @property
    def available(self):
        return None

    # <editor-fold desc="Trading fee">
    buy_fee = None
    buy_fee_tuple = None
    sell_fee = None
    tax = None

    # </editor-fold>

    def __init__(self, balance, day):
        self.balance = float(balance)
        self._total_asset = None

        self.stock_to_share = {}  # type: Dict[str, EmuShare]
        self.day = day
        self.buy_count = 0
        self.win_infos = []  # type: List[WinInfo]
        set_account_fee()

    def copy_for_day(self, day):
        ea = EmuAccount(self.balance, day)
        ea.stock_to_share = copy.deepcopy(self.stock_to_share)
        # Do NOT copy self.non_sell_stocks_to_amount = {}
        return ea

    def buy_stock(self, code, price, amount, entrust_type=None):
        self.buy_count += 1
        assert amount % 100 == 0, 'Not proper amount'
        need_money = round(price * amount * (1 + self.buy_fee), 3)
        assert self.balance >= need_money
        self.balance -= need_money
        self.balance = round(self.balance, 3)
        self.stock_to_share[code] = EmuShare(code, price, amount, self.day, cost_money=need_money)
        return self

    @property
    def available(self):
        return self.balance

    def sell_stock(self, code, price, amount=None, entrust_type=None):
        share = self.stock_to_share[code]
        cost_money = share.cost_money
        amount = share.amount

        sell_money = round(price * amount * (1 - self.sell_fee), 3)
        if not gdp.is_etf(code):
            sell_money = round(sell_money * (1 - self.tax), 3)

        self.balance += sell_money
        self.balance = round(self.balance, 3)
        del self.stock_to_share[code]
        self.win_infos.append(WinInfo(code, share.time, self.day, sell_money / cost_money - 1))

    def buy_at_most(self, code, price, entrust_type=None):
        amount = self.balance * self.buy_fee_tuple[1] // \
                 ((self.buy_fee_tuple[1] + self.buy_fee_tuple[0]) * price * 100)
        amount = 100 * int(amount)
        return self.buy_stock(code, price, amount)

    def sell_at_most(self, code, price, entrust_type=None):
        if code in self.stock_to_share:
            self.sell_stock(code, price, None)
        else:
            assert False, f'There is no {code} to share'

    def calc_total_asset(self):
        try:
            self._total_asset = self.balance
            for stock, share in self.stock_to_share.items():
                self._total_asset += gdp.open(stock, self.day) * share.amount
            return self._total_asset
        except KeyError:
            return None

    def __repr__(self):
        asset = -1.0 if self._total_asset is None else self._total_asset
        return f'TotalAssert:{asset: <12.12} Balance:{self.balance:<12} Stocks:{self.stock_to_share}'


class EmuDayAccounts:
    def __init__(self, date_range):
        self.date_range = date_range
        self.day_to_index = dict(zip(date_range, range(len(date_range))))
        self.accounts = [None] * len(date_range)  # type: List[EmuAccount]

    def account_of(self, day):
        index = self.day_to_index[day]
        if not self.accounts[index]:
            self.accounts[index] = self.accounts[index - 1].copy_for_day(day)
            self.accounts[index].day = day
        return self.accounts[self.day_to_index[day]]

    @property
    def init_account(self):
        return self.accounts[0]

    @init_account.setter
    def init_account(self, value):
        self.accounts[0] = value


def test_buy_etf():
    set_account_fee()
    ea = EmuAccount(100_025, 100_1025)
    ea.buy_stock('sh510900', 1, 100_000)
    assert_equal(ea.balance, 0)
    assert len(ea.stock_to_share) == 1
    assert ea.stock_to_share['sh510900'].amount == 100000


def test_sell_etf():
    ea = EmuAccount(0, None)
    ea.stock_to_share = {'sh510900': EmuShare('510900', 100000, 1, 19220101, 100000)}
    ea.sell_stock('sh510900', 1)
    assert ea.balance == 99975
    assert len(ea.stock_to_share) == 0


def test_sell_stock():
    ea = EmuAccount(0, '1900-01-01')
    ea.stock_to_share = {'sz000001': EmuShare('sz000001', 1, 100000, 19220101, 100000)}
    ea.sell_stock('sz000001', 1)
    assert len(ea.stock_to_share) == 0
    assert ea.balance == 99875.025


def test_buy_all():
    ea = EmuAccount(1, '1900-01-01')
    ea.balance = 100025
    ea.buy_at_most('510900', 1)
    assert_equal(ea.balance, 0)
    assert_equal(ea.stock_to_share['510900'].amount, 100000)
