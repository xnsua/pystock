import math

from stock_data_manager.classify import etf_stdcode_to_name

from ip.st import ClientOperBuy, ClientOperSell


def format_price(stock, price):
    if stock in etf_stdcode_to_name:
        price_str = str(round(price, 3))
    else:
        price_str = str(round(price, 2))
    assert math.isclose(float(price_str), price), f'{price} is not close to {price_str}'
    return price


def format_operation(oper):
    if isinstance(oper, ClientOperBuy):
        oper.price = format_price(oper.stock_code, oper.price)
    elif isinstance(oper, ClientOperSell):
        oper.price = format_price(oper.stock_code, oper.price)
