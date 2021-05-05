import pandas as pd
from pandas import DataFrame
import json
from janome.tokenizer import Tokenizer
from requests_oauthlib import OAuth1Session
from wordcloud import WordCloud
import emoji
import re
import csv

import config as cf

keysfile = '../twitter_API/key/keys.json'
signature = '#TweetFromPython'

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
    params = {'status': text + '\n' + signature}
    req = oauth.post(url, params)

    if req.status_code == 200:
        print('tweet succeed!')
    else:
        print('tweet failed')

def search_tweet(word, count, oauth):
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {
        'q': word,
        'count' : count,
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

def tweet_image(oauth, text, image_file):
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    url_text = "https://api.twitter.com/1.1/statuses/update.json"
    
    files = {"media" : open(image_file, 'rb')}
    req_media = oauth.post(url_media, files = files)
    if req_media.status_code != 200:
        print ('media upload failed: %s', req_media.text)
        exit()
        
    media_id = json.loads(req_media.text)['media_id']
    print ("Media ID: %d" % media_id)
    
    params = {'status': text + '\n' + signature, 'media_ids': [media_id]}
    req = oauth.post(url_text, params)

    if req.status_code == 200:
        print('tweet succeed!')
    else:
        print('tweet failed')

##################### Text Normalization #####################
def remove_emoji(text):
    return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI['en'])
def remove_url(text):
    return re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', text)
##################### Morph #####################
# Get Wakachigaki
def get_wakachi(list_text, word, hinshi=['名詞', '形容詞']):
    remove_words = ['こと', 'よう', 'そう', 'これ', 'それ', 'もの', 'ここ', 'さん', 'ちゃん',
                'ところ', 'とこ', 'の', 'ん', word]
    t = Tokenizer()
    wakachi = ''
    for text in list_text:
        malist = t.tokenize(text)
        for w in malist:
            word = w.surface
            part = w.part_of_speech
            hit = False
            for h in hinshi:
                hit = hit or (h in part)
            if not hit:
                continue
            if word not in remove_words:
                wakachi += word + ' '
    return wakachi

##################### Twitter Tools #####################
# Tweet Normalization
def normalize_tweets(tweets):
    normalized = []
    for tweet in tweets:
        text = tweet
        text = remove_emoji(text)
        text = remove_url(text)
        normalized.append(text)
    return normalized

# Initialize Negative-Positive Dictionary
pn_dic = {}
fp = open('../lib/pn.csv', 'rt', encoding='utf-8')
reader = csv.reader(fp, delimiter='\t')
for i, row in enumerate(reader):
  name = row[0]
  result = row[1]
  pn_dic[name] = result
# Color Function for Word Cloud
def get_pn_color(word, font_size, **kwargs):
    r, g, b = 0, 0, 0
    pn = 'e'
    if word in pn_dic:
        pn = pn_dic[word]
    if pn == 'p':
        b = 255
    elif pn == 'n':
        r = 255
    else:
        g = 255
    return (r, g, b)

# Word Cloud
def word_cloud(words, image_file, num,
                font_path='C:/Windows/Fonts/MSGOTHIC.TTC'):
    wordcloud = WordCloud(
            background_color='white', 
            color_func=get_pn_color,
            max_words=num,
            font_path=font_path,
            width=800, height=400).generate(words)
    wordcloud.to_file(cf.save_dir + image_file)
    return True
# Tweet Trends Words by Word Cloud
def tweetTrendWords(oauth, word, count=100, num=100, name='trend'):
    image_file = name + '.jpg'
    search = search_tweet(word, count, oauth)
    df_search = DataFrame.from_dict(search['statuses'])
    tweets = df_search['text'].tolist()
    tweets = normalize_tweets(tweets)
    # wards_count = count_words(tweets)
    # wakachi = get_wakachi(wards_count, num)
    wakachi = get_wakachi(tweets, word)
    word_cloud(wakachi, image_file, num)
    tweet_text = 'search word: {}\nsearch tweets num: {}\ntrend words num: {}'.format(word, count, num)
    tweet_image(oauth, tweet_text, cf.save_dir + image_file)

def main():
    keys = json.load(open(keysfile))
    twitter = create_oauth_session(keys)

    # text = 'tweet test'
    # tweet(twitter, text)

    search_words = ['ビットコイン', 'イーサリアム']
    search_num = 200
    trend_num = 200
    for word in search_words:
        image_name = word+'_{}-{}'.format(search_num, trend_num)
        tweetTrendWords(twitter, word, count=search_num, num=trend_num, name=image_name)

if __name__ == '__main__':
    main()