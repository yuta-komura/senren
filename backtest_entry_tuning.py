from lib import repository

DATABASE = "tradingbot"

while True:
    sql = "select date from backtest_entry order by date desc limit 1"
    be = repository.read_sql(database=DATABASE, sql=sql)
    if not be.empty:
        date = be.at[0, "date"]
        sql = "delete from backtest_entry where date < '{date}'"\
            .format(date=date)
        repository.execute(database=DATABASE, sql=sql, write=False)
