import tweepy
import os
import json

from pprint import pprint
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

######################################################################
### Variables
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

query = os.getenv("QUERY")
tweets_cnt = int(os.getenv("TWEETS_CNT"))


date = datetime.today().strftime('%Y%m%d')
month = datetime.today().strftime('%Y%m')
time = datetime.now().strftime('%H%M')

ROOT = os.getcwd()

### Authenticate to Twitter
client = tweepy.Client(bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret)


######################################################################
### Main function

def twitterbot(event, context):
    # Action_01: Collect Twitter raw data
    tweets_info = searchTweets(client, query, tweets_cnt)

    # Action_02: Post a new tweet
    text = 'I just collected ' + str(tweets_cnt) + ' tweets.'    
    Tweets_Create(text)

    # Action_03: retweet the first tweet of the collection
    text = 'retweet test'
    id = tweets_info['tweets'][0]['id']
    client.create_tweet(text=text, quote_tweet_id=id)


######################################################################
### functions  

## create tweets
def Tweets_Create(text):

    while len(text) > 280:
        tweet_1 = text[:280]
        client.create_tweet(text=tweet_1)
        text = text[280:]

    client.create_tweet(text=text)

    print("tweet posted!")


## collect tweets info
def searchTweets(client, query, tweets_cnt):

    tweet_fields=['author_id', 'created_at', 'lang', 'possibly_sensitive', 'source', 'geo', 'entities', 'public_metrics', 'context_annotations']
    user_fields=['id', 'name', 'username', 'created_at','profile_image_url','public_metrics']
    expansions = ['author_id', 'referenced_tweets.id', 'geo.place_id', 'attachments.media_keys', 'in_reply_to_user_id']
    start_time = None
    end_time = None

    tweets = tweepy.Paginator(client.search_recent_tweets, 
                    query=query, 
                    tweet_fields=tweet_fields, 
                    user_fields=user_fields,
                    expansions=expansions,
                    start_time=start_time,
                    end_time=end_time,
                    max_results=100).flatten(limit=tweets_cnt)
   
    tweets_info = []

    for tweet in tweets: 
        tweets_info.append(tweet.data)

    # from list to dict 
    # the following code which transfer list to dict is cited from TwitterCollector by Gene Moo Lee, Jaecheol Park and Xiaoke Zhang
    result = {}
    result['collection_type'] = 'recent post'
    result['query'] = query
    result['tweet_cnt'] = len(tweets_info)
    result['tweets'] = tweets_info

    # save result to file
    keyword=query.split(" ")[0]
    file_name = date + '_' + keyword +'_' + str(tweets_cnt) + '.json'
    path = ROOT + '/Data/' + month
    Save_Result_to_File(result,file_name, path)

    return result


## save result to file
def Save_Result_to_File(result,file_name, path):
    save_file = os.path.join(path, file_name)
    file_path = Path(save_file)
    file_path.parent.mkdir(exist_ok=True, parents=True)

    with open(file_path, 'w', encoding = 'utf-8') as file:
        file.write(json.dumps(result, indent=4))