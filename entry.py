from lib import message, repository


def save_entry(side):
    message.info(side, "entry")
    sql = "update entry set side='{side}'".format(side=side)
    repository.execute(database=DATABASE, sql=sql, write=False)


def reverse_side(side):
    if side == "BUY":
        return "SELL"
    else:  # side == "SELL"
        return "BUY"


def get_side():
    asset = 1000000
    sql = """
            select
                *
            from
                backtest_entry_analysis
            order by
                date
            """
    be = repository.read_sql(database=DATABASE, sql=sql)
    if be.empty:
        return None

    profits = []
    for i in range(len(be)):
        if i == 0:
            continue

        entry_position = be.iloc[i - 1]
        close_position = be.iloc[i]

        if entry_position["side"] == "BUY" and (
                close_position["side"] == "SELL" or close_position["side"] == "CLOSE"):

            amount = asset / entry_position["price"]
            profit = (amount * close_position["price"]) - asset

            profits.append(profit)
            asset += profit

        if entry_position["side"] == "SELL" and (
                close_position["side"] == "BUY" or close_position["side"] == "CLOSE"):

            amount = asset / entry_position["price"]
            profit = asset - (amount * close_position["price"])

            profits.append(profit)
            asset += profit

    side = be["side"].iloc[len(be) - 1]
    if sum(profits) < 0:
        side = reverse_side(side=side)
    return side


DATABASE = "tradingbot"

has_buy = False
has_sell = False
while True:
    side = get_side()

    if side == "BUY" and not has_buy:
        save_entry(side="BUY")
        has_buy = True
        has_sell = False

    if side == "SELL" and not has_sell:
        save_entry(side="SELL")
        has_buy = False
        has_sell = True
