import os

import pandas as pd
import json
import re
import unidecode

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

# Combine all files into a dataframe variable
dfs = []
for x in range(5, 10):
    # files.append(f'tweets_{x}_1830_2000.csv')
    df = pd.read_csv(f'./data/tweets/tweets_{x}_1700_2000.csv')
    dfs.append(df)

data = pd.concat(dfs)
from nltk.tokenize import word_tokenize

# -- 1. Remove duplicate tweets
data.drop_duplicates(subset='text', inplace=True)
data.dropna(subset=['text'], inplace=True)
# print(data.isna().any())
print(data)

# -- 2. Clean tweets
punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@'  # define a string of punctuation symbols

# negative words needed for analyzing general mood
custom_stopwords = list(stopwords.words('english'))
custom_stopwords = [w for w in custom_stopwords if w not in ('no', 'nor', 'not')]


def remove_accented_chars(tweet):
    """remove accented characters from text, e.g. café"""
    tweet = unidecode.unidecode(tweet)
    return tweet


# hasn’t -> has not
def expand_contractions(tweet):
    # specific
    tweet = re.sub(r"won\'t", "will not", tweet)
    tweet = re.sub(r"can\'t", "can not", tweet)

    # general
    tweet = re.sub(r"n\'t", " not", tweet)
    tweet = re.sub(r"\'re", " are", tweet)
    tweet = re.sub(r"\'s", " is", tweet)
    tweet = re.sub(r"\'d", " would", tweet)
    tweet = re.sub(r"\'ll", " will", tweet)
    tweet = re.sub(r"\'t", " not", tweet)
    tweet = re.sub(r"\'ve", " have", tweet)
    tweet = re.sub(r"\'m", " am", tweet)
    return tweet


def remove_links(tweet):
    """Takes a string and removes web links from it"""
    tweet = re.sub(r'http\S+', '', tweet)  # remove http links
    tweet = re.sub(r'bit.ly/\S+', '', tweet)  # remove bitly links
    tweet = tweet.strip('[link]')  # remove [links]
    tweet = re.sub(r'pic.twitter\S+', '', tweet)
    return tweet


def remove_users(tweet):
    """Takes a string and removes retweet and @user information"""
    tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet)  # remove re-tweet
    tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet)  # remove tweeted at
    return tweet


def remove_hashtags(tweet):
    """Takes a string and removes any hash tags"""
    tweet = re.sub('(#[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet)  # remove hash tags
    return tweet


def remove_av(tweet):
    """Takes a string and removes AUDIO/VIDEO tags or labels"""
    tweet = re.sub('VIDEO:', '', tweet)  # remove 'VIDEO:' from start of tweet
    tweet = re.sub('AUDIO:', '', tweet)  # remove 'AUDIO:' from start of tweet
    return tweet


def lemmatize(tokens):
    result = []
    # print(tokens)
    """Returns lemmatization of a token"""
    for token, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        # print(pos)
        WordNetLemmatizer().lemmatize(token, pos=pos)

        if token not in custom_stopwords:
            result.append(token)
    return result


def preprocess_tweet(tweet):
    """Main master function to clean tweets, stripping noisy characters, and tokenizing use lemmatization"""
    tweet = remove_accented_chars(tweet)
    tweet = expand_contractions(tweet)
    tweet = remove_users(tweet)
    tweet = remove_links(tweet)
    tweet = remove_hashtags(tweet)
    tweet = remove_av(tweet)
    tweet = tweet.lower()
    tweet = re.sub('[' + punctuation + ']+', ' ', tweet)  # strip punctuation
    tweet = re.sub('\s+', ' ', tweet)  # remove double spacing
    tweet = re.sub('([0-9]+)', '', tweet)  # remove numbers; numbers no info
    tweet_token_list = lemmatize(word_tokenize(tweet))  # apply lemmatization and tokenization
    tweet = ' '.join(tweet_token_list)
    return tweet


# print(data.text)
if __name__ == '__main__':
    # Only consider english tweet
    data = data[data['lang'] == 'en']
    print(len(data))  # 49355 -> 46313 after taking in only english tweets
    data['tokens'] = data.text.map(preprocess_tweet)
    # print(df.loc[df['text'] == '<br'])

    data.to_csv('./data/a4_prep_tweets.csv', encoding='utf-8', mode='w', index=False)
