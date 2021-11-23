import os
from datetime import timedelta, datetime

import numpy as np
import pandas as pd
import yfinance as yf

origin_csv_file = f'data/yfinance/origin_yfinance.csv'
preprocessed_csv_file = f'data/yfinance/preprocessed_yfinance.csv'


def get_original_data():
    df = pd.read_csv(origin_csv_file)
    return df


class YFiananceClient:
    def __init__(self, tickers: str):
        try:
            self.api = yf.download(tickers=tickers,
                                   start="2021-05-01",
                                   end="2021-10-01",

                                   # fetch data by interval (including intraday if period < 60 days)
                                   # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                   # (optional, default is '1d')
                                   interval="1d",

                                   # group by ticker (to access via data['SPY'])
                                   # (optional, default is 'column')
                                   group_by='ticker',
                                   )
            print(self.api)

            if not os.path.isfile(origin_csv_file):
                self.api.to_csv(origin_csv_file, encoding='utf-8')
            else:
                print('csv origin file exists.')

        except Exception as e:
            print("Error: Fetching Failed", e)

    def get_dates_sorted(self, date_in, date_out):
        # List date from date_in to date_out
        start = datetime.strptime(date_in, '%Y-%m-%d').date()
        end = datetime.strptime(date_out, '%Y-%m-%d').date()

        date_arr = [start + timedelta(x) for x in range(0, (end - start).days)]
        date_arr.sort()
        sorted_dates = [datetime.strftime(ts, "%Y-%m-%d") for ts in date_arr]
        return {'Date': sorted_dates}

    def merge_by_dates(self):
        # Create a dataframe for closing price with missing dates
        data = pd.read_csv(origin_csv_file)

        date_in = '2021-04-30'
        date_out = '2021-09-30'
        sorted_dates = self.get_dates_sorted(date_in, date_out)

        df1 = pd.DataFrame(data[['Date', 'Adj Close']])
        df2 = pd.DataFrame(sorted_dates)

        left_join = pd.merge(df2, df1, on='Date', how='left')
        return left_join

    def fill_up_gaps(self):
        # Fill up the gap by finding previous index and next index price to apply (x+y)/2
        data = self.merge_by_dates()

        [null_idx] = np.where(data['Adj Close'].isnull())
        for i in range(len(null_idx)):

            before = data.iloc[null_idx[i] - 1]['Adj Close']
            after = 0

            # Check up to 3days after missing value
            if i != (len(null_idx) - 1):
                # If next day value is null
                if np.isnan(data.iloc[null_idx[i] + 1]['Adj Close']):
                    # If 2nd next value is null
                    if np.isnan(data.iloc[null_idx[i] + 2]['Adj Close']):
                        after = data['Adj Close'][null_idx[i] + 3]
                    else:
                        after = data['Adj Close'][null_idx[i] + 2]
                else:
                    after = data['Adj Close'][null_idx[i] + 1]
            else:
                # Check if null_idx is the last value
                after = data['Adj Close'][null_idx[i] + 1]

            # if after has value, apply the equation and insert into data
            if not np.isnan(after):
                data.at[[null_idx[i]], 'Adj Close'] = (before + after) / 2

        # print(data)
        origin = get_original_data()
        data = data.merge(origin[['Date', 'Close', 'Volume']], how='left', on='Date')

        # fill with previous values in adj close and volume
        data.fillna(method='ffill', inplace=True)
        print(data)

        # Missing value more than 4 days in a row will not produce a file
        if not data['Close'].isnull().values.any():
            data.to_csv(preprocessed_csv_file, encoding='utf-8', mode='w', index=False)
        return data


if __name__ == '__main__':
    api = YFiananceClient('MSFT')
    api.fill_up_gaps()
