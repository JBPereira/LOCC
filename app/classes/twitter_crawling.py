import tweepy
from tweepy import OAuthHandler
import os


class TwitterCrawler(object):
    def __init__(self):
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
        access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        self.api = tweepy.API(auth)
        self.flood_words = ['hoosbui', 'inundatie', 'onderstroming', 'onderwaterzetting',
                            'plensbui', 'stortbui', 'vloed', 'watersnood', 'watervloed', 'wolkbreuk']

    def get_flood_related_tweets(self):

        flood_search = []

        for word in self.flood_words:
            word_search = self.api.search(word)
            for status in word_search:
                flood_search.append({'text':status.text, 'location': status.author.location})

        return flood_search

tweety = TwitterCrawler()
flood = tweety.get_flood_related_tweets()
print(flood)