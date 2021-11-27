import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
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


def get_idf_value(dataset):
    print('calling from tweet_sa')
    """TF-IDF vectorize"""
    # df = pd.read_csv('./data/sa_tweets.csv')
    doc_tokens = dataset['tokens'].ravel()
    # print(doc_tokens)
    print(doc_tokens.shape)

    # instantiate CountVectorizer and generate word counts
    cv = CountVectorizer()
    word_count_vector = cv.fit_transform(doc_tokens)
    print(word_count_vector.shape)

    # Compute IDF value
    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(word_count_vector)
    df_idf = pd.DataFrame(tfidf_transformer.idf_, index=cv.get_feature_names_out(), columns=["idf_weights"])
    # Lower the IDF value, the less unique
    df_idf = df_idf.sort_values(by=['idf_weights'], ascending=False)

    # Change name for word cloud
    df_idf.index.name = 'word'
    df_idf.rename(columns={'idf_weights': 'size'}, inplace=True)
    df_idf.reset_index(level=0, inplace=True)
    json_out = df_idf.to_json(orient='records')[1:-1].replace('},{', '} {')

    # print(json_out)
    return json_out, doc_tokens.shape, word_count_vector.shape


if __name__ == '__main__':
    df = pd.read_csv('data/a4_prep_tweets.csv')

    # To get subjectivity and polarity, tokens should not be null
    df['tokens'] = df['tokens'].fillna(' ')
    print(df['tokens'].isnull().sum())

    df['tb_subjectivity'] = df['tokens'].apply(get_subjectivity)
    df['tb_polarity'] = df['tokens'].apply(get_polarity)
    df['tb_analysis'] = df['tb_polarity'].apply(get_analysis)
    df.to_csv('./data/sa_tweets.csv', encoding='utf-8', mode='w', index=False)
