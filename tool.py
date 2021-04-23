import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
import time
import datetime

import poloniex

import config as cf

# Load price from Poloniex
def load_chart(
    price='USDT_BTC',
    price_type='open',
    data_range=365
    ):
    polo = poloniex.Poloniex()
    period = polo.DAY # period of data
    end = time.time()
    start = end - period * data_range

    chart = polo.returnChartData(price, period=period, start=start, end=end)
    df = DataFrame.from_dict(chart)

    return df

def get_price(
    price='USDT_BTC',
    price_type='open',
    data_range=365
    ):
    df = load_chart(price=price, price_type=price_type, data_range=data_range)

    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    # timestamp -> year/month/day
    date = [datetime.datetime.fromtimestamp(timestamp[i]).date() for i in range(len(timestamp))]
    # date_str = [date[i].strftime('%Y-%m-%d') for i in range(len(date))]

    price = df[price_type].astype(float).values.tolist()

    return (date, price)

# Plot graph
def plot_graph(
    price='USDT_BTC',
    price_type='open',
    data_range=365,
    name='chart-BTC.png'
    ):
    date, price = get_price(
        price=price,
        price_type=price_type,
        data_range=data_range)
    plt.plot(date, price)
    plt.savefig(cf.save_dir + name)

# Plot CandleStick Chart
def plot_candlestick(
    price='USDT_BTC',
    price_type='open',
    data_range=100,
    name='candlestick_BTC.png'
    ):
    df = load_chart(price=price, price_type=price_type, data_range=data_range)

    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    # timestamp -> year/month/day
    date = [datetime.datetime.fromtimestamp(timestamp[i]).date() for i in range(len(timestamp))]
    df['date'] = date

    df.index = pd.to_datetime(df['date'])
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = df.astype(float)

    mpf.plot(df, type='candle', figratio=(12,4), savefig=cf.save_dir + name)

