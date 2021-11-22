import pandas as pd
from textblob import TextBlob


def get_subjectivity(tweet):
    return TextBlob(tweet).subjectivity


def get_polarity(tweet):
    return TextBlob(tweet).polarity


def get_analysis(polarity_score):
    if polarity_score < 0:
        return '-1'  # Negative
    elif polarity_score == 0:
        return '0'  # Neutral
    else:
        return '1'  # Positive


if __name__ == '__main__':
    df = pd.read_csv('data/a4_prep_tweets.csv')

    # To get subjectivity and polarity, tokens should not be null
    df['tokens'] = df['tokens'].fillna(' ')
    print(df['tokens'].isnull().sum())

    df['tb_subjectivity'] = df['tokens'].apply(get_subjectivity)
    df['tb_polarity'] = df['tokens'].apply(get_polarity)
    df['tb_analysis'] = df['tb_polarity'].apply(get_analysis)
    df.to_csv('./data/sa_tweets.csv', encoding='utf-8', mode='w', index=False)
