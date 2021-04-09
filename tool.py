import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import datetime

import poloniex


def load_price(price='USDT_BTC',
                price_type='open',
                data_range=365
                ):
    polo = poloniex.Poloniex()
    period = polo.DAY # period of data
    end = time.time()
    start = end - period * data_range

    chart = polo.returnChartData(price, period=period, start=start, end=end)
    df = DataFrame.from_dict(chart)

    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    # timestamp -> year/month/day
    date = [datetime.datetime.fromtimestamp(timestamp[i]).date() for i in range(len(timestamp))]
    date = [date[i].strftime('%Y-%m-%d') for i in range(len(date))]

    price = df[price_type].astype(float).values.tolist()

    return (date, price)