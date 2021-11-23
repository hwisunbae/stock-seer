# https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search#DataEndpoint
# https://www.justintodata.com/twitter-sentiment-analysis-python/#step-3-process-the-data-and-apply-the-textblob-model

import os
from os.path import join, dirname
from dotenv import load_dotenv

from TwitterAPI import TwitterAPI
import pandas as pd
import json
import calendar

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("CONSUMER_API_KEY")
API_KEY_SECRET = os.environ.get("CONSUMER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")



# Global variables for getting tweets between time periods
year = 2021
month = 5
time_end = '2000'
time_start = '1700'

json_filename = f'./data/tweets/tweets_{month}_{time_start}_{time_end}.json'
csv_filename = f'./data/tweets/tweets_{month}_{time_start}_{time_end}.csv'


def get_all_tweets(toDate, json_filename, csv_filename):
    data = []

    SEARCH_TERM = "microsoft I'm OR microsoft feel OR microsoft am OR microsoft being OR microsoft be"
    PRODUCT = 'fullarchive'
    LABEL = 'temp'

    try:
        api = TwitterAPI(API_KEY,
                         API_KEY_SECRET,
                         ACCESS_TOKEN,
                         ACCESS_TOKEN_SECRET)
        print('API connected', api)
    except Exception as e:
        print("Error: Authentication Failed", e)

    r = api.request('tweets/search/%s/:%s' % (PRODUCT, LABEL),
                    {'query': SEARCH_TERM,
                     'maxResults': '500',
                     'fromDate': f'20210501{time_start}',  # predict date : 2021-05-01 ~ 2021-09-30
                     'toDate': toDate})

    # Dictionary for json
    for item in r:
        row = {
            'id': item['id'],  # The direct link is of the form: https://twitter.com/i/web/status/{tweet-status-id}
            'created_at': item['created_at'],
            'user_name': item['user']['name'],
            'text': item['text'],
            'lang': item['lang']
        }
        data.append(row)

    # Covert dict to json
    print(data)
    with open(json_filename, 'w', encoding='utf8') as f_out:
        json.dump(data, f_out)

    # Covert json to csv
    with open(json_filename, encoding='utf-8-sig') as f_in:
        df = pd.read_json(f_in)

    if os.path.isfile(csv_filename):
        df.to_csv(csv_filename, encoding='utf-8', mode='a', index=False, header=False)
    else:
        df.to_csv(csv_filename, encoding='utf-8', mode='a', index=False)


# Get tweets during specified period within specified time. The latest tweets are retrieved.
if __name__ == '__main__':
    num_days = calendar.monthrange(year, month)

    for x in range(int(str(year) + '%02d' % month + str(num_days[1]) + time_end),
                   (int(str(year) + '%02d' % month + '01' + time_end)) - 1, -10000):
        print(x)
        get_all_tweets(x, json_filename, csv_filename)
