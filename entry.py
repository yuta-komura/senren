from lib import message, repository


def save_entry(side):
    message.info(side, "entry")
    sql = "update entry set side='{side}'".format(side=side)
    repository.execute(database=DATABASE, sql=sql, write=False)


def get_side():
    sql = "select * from backtest_entry where side != 'CLOSE' and size <= 0.01 order by date desc limit 1"
    be = repository.read_sql(database=DATABASE, sql=sql)
    if be.empty:
        return None
    else:
        return be.at[0, "side"]


DATABASE = "tradingbot"

has_buy = False
has_sell = False
is_first = True
while True:
    side = get_side()

    if side == "SELL" and not has_buy:
        if is_first:
            is_first = False
        else:
            save_entry(side="BUY")
        has_buy = True
        has_sell = False

    if side == "BUY" and not has_sell:
        if is_first:
            is_first = False
        else:
            save_entry(side="SELL")
        has_buy = False
        has_sell = True
