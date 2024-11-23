#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !pip install pandas
import pandas as pd
import time, datetime, sys
import os, pathlib
from keys import twelveDataKey as api_key

import requests
import io
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

def request_stock_data(ticker, start_date:datetime, end_date:datetime, interval='15min'):
  '''
  Query the API and return a df of the open price of a given ticker between the start_date and end_date
  '''
  url = 'https://api.twelvedata.com/time_series'
  params = {
      'symbol':ticker,
      'interval':interval,
      'start_date':start_date.strftime('%Y-%m-%d %H:%M:%S'),
      'end_date':end_date.strftime('%Y-%m-%d %H:%M:%S'),
      'apikey':api_key,
      'format':'CSV',
      'delimiter':',',
      'order':'ASC'
  }
  urlData = requests.get(url, params).content
  df = pd.read_csv(io.StringIO(urlData.decode('utf-8')),delimiter=',', index_col='datetime')
  df.drop(columns=['high','low','close','volume'], inplace=True)
  df.rename(columns={'open':ticker}, inplace=True)
  return df

def collect_stock_data_new(tickers:list, start_date:datetime):
  '''
  Collects up to 5,000 days of stock data for all of a list of tickers from start_date and returns as a single dataframe. If more than 8 tickers, only queries every 60 seconds due to API provider limit of 8 requests per minute.
  '''
  full_df = pd.DataFrame()
  for i, ticker in enumerate(tickers):
    interval_end = start_date + timedelta(days=5000)
    ticker_df = request_stock_data(ticker, start_date, interval_end, interval='1day')
    if (i+1) % 8 == 0:
      print('Waiting 60s')
      time.sleep(60)
    if full_df.empty:
      full_df = ticker_df
    else:
      full_df = full_df.join(ticker_df)
  return full_df

tech_df = collect_stock_data_new(['AAPL', 'MSFT'], datetime(2024, 6, 1, 8))

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

dates = tech_df.index.rename('Date')
init_date = list(dates)[0]
last_hist_date = list(dates)[-1]


init_delay_seconds = 30
interval = 5

scaler = tech_df['AAPL'][init_date]/tech_df['MSFT'][init_date]
aapl  = tech_df['AAPL']
msft  = tech_df['MSFT']
tech_df['scaledMSFT'] = msft*scaler

print ('Sending daily AAPL and MSFT prices from %10s to %10s ...' % (str(init_date)[:10], str(last_hist_date)[:10]), flush=True, file=sys.stderr)
print ("... each day's data sent every %d seconds ..." % (interval), flush=True, file=sys.stderr)
print ('... beginning in %02d seconds ...' % (init_delay_seconds), flush=True, file=sys.stderr)
print ("... MSFT prices adjusted to match AAPL prices on %10s ..."  % (init_date), flush=True, file=sys.stderr)

from tqdm import tqdm
for left in tqdm(range(init_delay_seconds)):
    time.sleep(0.5)

for date in list(dates):       
    print ('%10s\t%.4f\t%.4f' % (str(date)[:10], tech_df['AAPL'][date], tech_df['scaledMSFT'][date]), flush=True)
    time.sleep(float(interval))

exit(0)