import datetime
import time

from lib import repository


def save_entry(date, side, price):
    sql = "insert into backtest_entry_analysis values ('{date}','{side}',{price})"\
        .format(date=date, side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, write=False)


def get_order_data(side):
    sql = "select * from ticker"
    ticker = repository.read_sql(database=DATABASE, sql=sql).iloc[0]
    if side == "BUY":
        order_price = ticker["best_bid"] + 1  # 1361825
    else:  # SELL
        order_price = ticker["best_ask"] - 1  # 1361969
    order_date = datetime.datetime.now()
    return order_date, order_price


def buy():
    side = "BUY"
    while True:
        date, price = get_order_data(side=side)
        time.sleep(1)
        sql = """
                select
                    *
                from
                    execution_history
                where
                    side = 'SELL'
                    and date > '{date}'
                    and price <= '{price}'
                """.format(date=date, price=price)
        eh = repository.read_sql(database=DATABASE, sql=sql)
        if eh.empty:
            time.sleep(1)
        else:
            date = datetime.datetime.now()
            save_entry(date, side, price)
            break


def sell():
    side = "SELL"
    while True:
        date, price = get_order_data(side=side)
        time.sleep(1)
        sql = """
                select
                    *
                from
                    execution_history
                where
                    side = 'BUY'
                    and date > '{date}'
                    and price >= '{price}'
                """.format(date=date, price=price)
        eh = repository.read_sql(database=DATABASE, sql=sql)
        if eh.empty:
            time.sleep(1)
        else:
            date = datetime.datetime.now()
            save_entry(date, side, price)
            break


def get_side():
    sql = "select * from backtest_entry where side != 'CLOSE' and size <= 0.01 limit 1"
    be = repository.read_sql(database=DATABASE, sql=sql)
    if be.empty:
        return None
    else:
        return be.at[0, "side"]


DATABASE = "tradingbot"

has_buy = False
has_sell = False
while True:
    side = get_side()

    if side == "BUY" and not has_buy:
        buy()
        has_buy = True
        has_sell = False

    if side == "SELL" and not has_sell:
        sell()
        has_buy = False
        has_sell = True
