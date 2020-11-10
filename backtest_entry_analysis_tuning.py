import datetime
import time

from lib import repository

DATABASE = "tradingbot"

while True:
    date = datetime.datetime.now() - datetime.timedelta(hours=3)
    sql = "delete from backtest_entry_analysis where date < '{date}'"\
        .format(date=date)
    repository.execute(database=DATABASE, sql=sql, write=False)
    time.sleep(60)
