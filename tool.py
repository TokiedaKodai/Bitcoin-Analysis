import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
import time
import datetime
import os

import poloniex

import config as cf

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load price from Poloniex
def loadChart(
    price='USDT_BTC',
    data_range=365
    ):
    polo = poloniex.Poloniex()
    period = polo.DAY # period of data
    end = time.time()
    start = end - period * data_range

    chart = polo.returnChartData(price, period=period, start=start, end=end)
    df = DataFrame.from_dict(chart)
    return df

# Timestamp to Date (year/month/day)
def timestamp2date(timestamp):
    return [datetime.datetime.fromtimestamp(timestamp[i]).date() for i in range(len(timestamp))]
# Date to String
def date2str(date):
    return [date[i].strftime('%Y-%m-%d') for i in range(len(date))]

# Get price and date values
def getPrice(
    price='USDT_BTC',
    price_type='open',
    data_range=365
    ):
    df = loadChart(price=price, data_range=data_range)
    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    date = timestamp2date(timestamp) # timestamp -> year/month/day
    price = df[price_type].astype(float).values.tolist()
    return (date, price)

# Plot graph
def plotGraph(
    price='USDT_BTC',
    price_type='open',
    data_range=365,
    name='chart-BTC.png'
    ):
    date, price = getPrice(
        price=price,
        price_type=price_type,
        data_range=data_range)
    plt.plot(date, price)
    plt.savefig(cf.save_dir + name)

# Plot CandleStick Chart
def plotCandlestick(
    price='USDT_BTC',
    price_type='open',
    data_range=100,
    name='candlestick_BTC.png'
    ):
    df = loadChart(price=price, data_range=data_range)
    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    df['date'] = timestamp2date(timestamp) # timestamp -> year/month/day

    df.index = pd.to_datetime(df['date'])
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = df.astype(float)

    mpf.plot(df, type='candle', figratio=(12,4), savefig=cf.save_dir + name)

# Plot Technical Chart
def plotTechnical(
    price='USDT_BTC',
    price_type='open',
    data_range=100,
    name='technical_BTC.png'
    ):
    # data_range+50 to calcurate SMA50
    df = loadChart(price=price, data_range=data_range+50)
    timestamp = df['date'].values.tolist() # Series -> ndarray -> list
    date = timestamp2date(timestamp) # timestamp -> year/month/day
    df = df.astype(float)
    df['date'] = date

    # Calcurate EMA20 and SMA50
    df['EMA20'] = df['open'].ewm(span=20).mean()
    df['SMA50'] = df['open'].rolling(window=50).mean()
    # Calcurate Bollinger Band
    r = df['open'].rolling(10)
    df['upper'] = r.mean() + 2 * r.std()
    df['lower'] = r.mean() - 2 * r.std()

    df = df.tail(data_range)
    df.index = pd.to_datetime(df['date'])
    df = df[['open', 'high', 'low', 'close', 'volume', 'EMA20', 'SMA50', 'upper', 'lower']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'EMA20', 'SMA50', 'upper', 'lower']

    # Plot
    addplot = mpf.make_addplot(df[['EMA20', 'SMA50']])
    fig, axes = mpf.plot(
        df, type='candle', addplot=addplot, volume=True, 
        fill_between=dict(y1=df['lower'].values, y2=df['upper'].values, color='lightblue', alpha=.3),
        style='charles', returnfig=True, figratio=(12,8), savefig=cf.save_dir + name)
    axes[0].legend(['EMA20', 'SMA50'], loc=2)
    fig.savefig(cf.save_dir + name)