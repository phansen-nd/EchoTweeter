#!/usr/bin/python -tt

# Patrick Hansen
# 11/29/16
# bot.py - a Python script to run a Twitter bot.

import tweepy, time, sys, json, os
from keys import keys
from random import randint
from datetime import datetime

# Extract constants from external source file.
CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

# Custom listener object to listen to Tweets from one handle.
class UserStreamListener(tweepy.StreamListener):

    def __init__(self, api, sample_responses, target_user_id):
        self.api = api
        self.sample_responses = sample_responses
        self.target_user_id = target_user_id

    def on_status(self, status):
        print("Status update: ", status.text)

    def on_error(self, status_code):
        if status_code == 420:
            print("\nRate limited.\n")
            return False
        print(status_code)

    def on_data(self, data):
        obj = json.loads(data)

        tweet_id = obj['id']
        tweet_text = obj['text']
        tweet_sender = obj['user']['screen_name']
        tweet_sender_id = obj['user']['id']

        if str(tweet_sender_id) == self.target_user_id:
            status = "@" + (tweet_sender) + " " + self.pickResponse()

            # Tweet a reply.
            self.api.update_status(status, tweet_id)

            # Print a log.
            self.createFormattedLogStatement(tweet_sender, tweet_text, status)

    def pickResponse(self):
        i = randint(0, len(self.sample_responses) - 1)
        return self.sample_responses[i].rstrip()

    def createFormattedLogStatement(self, sender, text, reply):
        print('\n', sender, ' tweeted:\n\n"', text, '"\n\nYou replied:\n\n"', reply, '"\n\nat ', str(datetime.now()), '\n')


if __name__ == "__main__":

    # Parse CL input.
    tweetfile = str(sys.argv[1])
    handlefile = str(sys.argv[2])
    filename = open(tweetfile, 'r')
    tweets = filename.readlines()
    filename.close()
    filename = open(handlefile, 'r')
    handles = filename.readlines()
    filename.close()

    # Set up auth.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Set up REST API.
    api = tweepy.API(auth)
    user = api.get_user(handles[0])
    user_id = str(user.id)
    # TODO error handle for unknown handle.

    # Set up listener.
    listener = UserStreamListener(api, tweets, user_id)
    stream = tweepy.Stream(auth, listener)

    # Start streaming and exit gracefully if asked.
    try:
        stream.filter(follow=[user_id]) # can add aync=True option
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
