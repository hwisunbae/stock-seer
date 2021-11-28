import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


# This function "window_data" accepts the column number for the features (X) and the target (y)
# It chunks the data up with a rolling window of Xt-n to predict Xt
# It returns a numpy array of X any y
def window_data(df, window, feature_col_number1, feature_col_number2, feature_col_number3, target_col_number):
    # Create empty lists "X_polarity", "X_volume", "X_close" and y
    X_close = []
    X_polarity = []
    X_volume = []
    y = []

    for i in range(len(df) - window):  # 151 - 3 = 148
        # Get polarity, tw_vol, close and target in the loop
        polarity = df.iloc[i:(i + window), feature_col_number1]
        tw_vol = df.iloc[i:(i + window), feature_col_number2]
        close = df.iloc[i:(i + window), feature_col_number3]
        target = df.iloc[(i + window), target_col_number]

        # Append values in the lists
        X_polarity.append(polarity)
        X_volume.append(tw_vol)
        X_close.append(close)
        y.append(target)

    return np.hstack((X_close, X_polarity, X_volume)), np.array(y).reshape(-1, 1)


def get_data(obj_tweet_pol, obj_tweet_vol, obj_stock):
    """ Data ready for feature engineering """

    # Dev purpose
    # df_tweet = pd.read_csv('data/sa_tweets.csv')
    # df_stock = pd.read_csv('data/yfinance/preprocessed_yfinance.csv')

    # Concatenate df_pol, df_vol and df_stock
    df_pol = pd.DataFrame(list(obj_tweet_pol))
    df_vol = pd.DataFrame(list(obj_tweet_vol))
    df_pol['date'] = df_pol['date'].astype(str).apply(lambda x: str(x)[:10])
    df_vol['date'] = df_vol['date'].astype(str).apply(lambda x: str(x)[:10])
    # print(df_pol)
    # print(df_vol)

    df_pol = df_pol.merge(df_vol, how='inner', on='date')
    # print(df_pol)

    # normalize polarity value
    df_pol_max = df_pol['total_polarity'].max()
    df_pol_min = df_pol['total_polarity'].min()
    df_pol['total_polarity'] = (df_pol['total_polarity'] - df_pol_min) / df_pol_max
    # print(df_pol)

    df_stock = pd.DataFrame(list(obj_stock))
    df_stock['date'] = df_stock['date'].astype(str)
    # print(df_stock)

    df = df_pol.merge(df_stock, how='inner', on='date')
    # print(df)

    df['pct_change'] = df['adj_close'].pct_change()
    df.dropna(inplace=True)
    df.set_index('date', inplace=True)
    print('Calling from m__')
    print(df)

    return df


def get_feature_x_target_y(df):
    """ Predict Closing Prices using a 3 day window of previous closing prices"""
    window_size = 3

    feature_col_number1 = 0
    feature_col_number2 = 1
    feature_col_number3 = 2
    target_col_number = 2
    X, y = window_data(df, window_size, feature_col_number1, feature_col_number2, feature_col_number3,
                       target_col_number)  # (148, 9), (148, 1)

    # Use 80% of the data for training and the remainder for testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=5)
    return X_train, X_test, y_train, y_test
