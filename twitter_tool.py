import pandas as pd
from pandas import Series, DataFrame
import json
from janome.tokenizer import Tokenizer
from requests_oauthlib import OAuth1Session
from wordcloud import WordCloud
import emoji
import re

keysfile = '../../twitter_API/key/keys.json'

##################### Twitter API #####################
def create_oauth_session(oauth_key_dict):
    oauth = OAuth1Session(
        oauth_key_dict['consumer_key'],
        oauth_key_dict['consumer_secret'],
        oauth_key_dict['access_token'],
        oauth_key_dict['access_token_secret']
    )
    return oauth

def tweet(oauth, text):
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    params = {'status': text + '\n#TweetFromBot'}
    req = oauth.post(url, params)

    if req.status_code == 200:
        print('tweet succeed!')
    else:
        print('tweet failed')

def tweet_search(search_word, num, oauth):
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {
        'q': search_word,
        'count' : num,
        'result_type' : 'recent',
        'exclude': 'retweets',
        'lang' : 'ja'
        }
    responce = oauth.get(url, params=params)
    if responce.status_code != 200:
        print("Error code: %d" %(responce.status_code))
        return None
    tweets = json.loads(responce.text)
    return tweets

##################### Text Normalization #####################
def remove_emoji(text):
    return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI['en'])

def remove_url(text):
    return re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', text)

##################### Twitter Tools #####################
def normalize_tweets(tweets):
    normalized = []
    for tweet in tweets:
        text = tweet
        text = remove_emoji(text)
        text = remove_url(text)
        normalized.append(text)
    return normalized


def main():
    keys = json.load(open(keysfile))
    oauth = create_oauth_session(keys)

    # text = 'tweet test'
    # tweet(oauth, text)

    search_word = 'ビットコイン'
    search_num = 10
    search = tweet_search(search_word, search_num, oauth)
    df_search = DataFrame.from_dict(search['statuses'])
    tweets = df_search['text'].tolist()

if __name__ == 'main':
    main()