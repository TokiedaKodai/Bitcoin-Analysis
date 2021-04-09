import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import tool

date, price = tool.load_price()
print(date[:5])
print(price[:5])

plt.plot(date, price)
plt.savefig('chart-BTC.png')
