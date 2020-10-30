import datetime

from lib import repository

DATABASE = "tradingbot"

while True:
    date = datetime.datetime.now() - datetime.timedelta(minutes=1)
    sql = "delete from execution_history where date < '{date}'"\
        .format(date=date)
    repository.execute(database=DATABASE, sql=sql, write=False)
