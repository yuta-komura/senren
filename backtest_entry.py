import datetime
import time

import numpy as np
import pandas as pd

from lib import repository


def save_entry(date, side, price, size=0, basis_price=None):
    sql = "insert into backtest_entry values ('{date}','{side}',{price},{size})"\
        .format(date=date, side=side, price=price, size=size)
    repository.execute(database=database, sql=sql, write=False)
    return {
        "date": date,
        "side": side,
        "price": price,
        "size": size,
        "basis_price": basis_price}


def get_order_data(side):
    sql = "select * from ticker"
    ticker = repository.read_sql(database=database, sql=sql).iloc[0]
    if side == "BUY":
        order_price = ticker["best_bid"]  # 1361825
    else:  # SELL
        order_price = ticker["best_ask"]  # 1361969
    order_date = datetime.datetime.now()
    return order_date, order_price


database = "tradingbot"
pd.set_option('display.max_columns', 100000)
pd.set_option('display.max_rows', 100000)

diff_ratio = 0.01

entry = None
befor_minute = None
while True:
    if entry:
        if entry["side"] == "BUY":
            side = "SELL"
            date = entry["date"]
            price = entry["basis_price"] * (1 + (diff_ratio / 100))

            size = entry["size"]
            if size > 0.01:
                order_date, order_price = get_order_data(side="SELL")
                date = order_date
                price = order_price - 1
                time.sleep(2)

            elapsed_sec = (datetime.datetime.now() - date).seconds
            if elapsed_sec >= 1800:
                order_date, order_price = get_order_data(side="BUY")
                time.sleep(2)
                save_entry(order_date, "CLOSE", order_price)
                entry = None
                continue

            price = int(price)
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
            eh = repository.read_sql(database=database, sql=sql)
            if eh.empty:
                pass
            else:
                date = datetime.datetime.now()
                save_entry(date, "CLOSE", price)
                entry = None
                continue
        else:  # entry["side"] == "SELL"
            side = "BUY"
            date = entry["date"]
            price = entry["basis_price"] * (1 - (diff_ratio / 100))

            size = entry["size"]
            if size > 0.01:
                order_date, order_price = get_order_data(side="BUY")
                date = order_date
                price = order_price + 1
                time.sleep(2)

            elapsed_sec = (datetime.datetime.now() - date).seconds
            if elapsed_sec >= 1800:
                order_date, order_price = get_order_data(side="SELL")
                time.sleep(2)
                save_entry(order_date, "CLOSE", order_price)
                entry = None
                continue

            price = int(price)
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
            eh = repository.read_sql(database=database, sql=sql)
            if eh.empty:
                pass
            else:
                date = datetime.datetime.now()
                save_entry(date, "CLOSE", price)
                entry = None
                continue
    else:
        befor_minute = datetime.datetime.now().minute

        side = "BUY"
        date, price = get_order_data(side=side)

        limits = []
        for i in range(1, 37):
            p = price * (1 - ((diff_ratio + (0.01 * (i - 1))) / 100))
            limits.append(int(p))

        time.sleep(1)
        sql = """
                select
                    price
                from
                    execution_history
                where
                    side = 'SELL'
                    and date > '{date}'
                    and price <= '{price}'
                """.format(date=date, price=limits[0])
        eh = repository.read_sql(database=database, sql=sql)
        if eh.empty:
            time.sleep(60)
        else:
            established = []
            for limit in limits:
                if not eh[eh["price"] <= limit].empty:
                    established.append(limit)

            date = datetime.datetime.now()
            price = int(np.average(established))

            size = 0.01 * len(established)
            entry = save_entry(date, side, price, size, limits[0])
            continue

        side = "SELL"
        date, price = get_order_data(side=side)

        limits = []
        for i in range(1, 37):
            p = price * (1 + ((diff_ratio + (0.01 * (i - 1))) / 100))
            limits.append(int(p))

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
                """.format(date=date, price=limits[0])
        eh = repository.read_sql(database=database, sql=sql)
        if eh.empty:
            time.sleep(60)
        else:
            established = []
            for limit in limits:
                if not eh[eh["price"] >= limit].empty:
                    established.append(limit)

            date = datetime.datetime.now()
            price = int(np.average(established))
            size = 0.01 * len(established)
            entry = save_entry(date, side, price, size, limits[0])
            continue
