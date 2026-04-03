import yfinance as yf
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


# getting data from yahoo trhough thier API

tickers = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL",
    "TSLA","META","JPM","V","UNH"
]

df = yf.download(
    
    tickers,
    start="2020-01-01",
    end="2026-01-01",
    group_by="ticker"
)

# check data frame -> be consistent with naming the data frame 
df.head()

# length of data 
print(len(df) , "this is the length of my data ")

print('This is the first test to take our project into production')

# flatten multi-index
df.columns = [f"{c[0]}_{c[1]}" for c in df.columns]

# ✅ ALWAYS WORKS (Close exists)
df_prices = df.filter(like='_Close')

# clean names
df_prices.columns = [c.replace('_Close','') for c in df_prices.columns]

# sanity
print("df_prices shape:", df_prices.shape)

print("PRICES SHAPE:", df_prices.shape)
print(df_prices.head())

df_returns = df_prices.pct_change()

print("RETURNS SHAPE:", df_returns.shape)
print(df_returns.head())