# This app serves quotes from famous female technologists by author and topic,
# and serves bios by author.

# [START app]
import csv
import logging
import random
import unicodedata
import json

from flask import Flask, request, make_response
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# List of (quote, author, (topic1, topic2, ...)) tuples.
quotes = []

# Map from author string to list of quote objects.
quotes_by_author = {}

# Map from topic string to list of quote objects.
quotes_by_topic = {}

# Map from author to bio.
bio_by_author = {}

# Read in quotes and bios.
with open('quotes.csv', 'rb') as quotes_file:
  quotes_reader = csv.reader(quotes_file)
  first_row = True
  for row in quotes_reader:
    if first_row:
      first_row = False
      continue
    quote = row[0]
    author = row[1].lower()
    bio = row[4]
    topics = tuple(row[7].split(','))
    quote_object = (quote, author, topics)
    quotes.append(quote_object)
    if author not in quotes_by_author:
      quotes_by_author[author] = []
    quotes_by_author[author].append(quote_object)
    for topic in list(topics):
      topic = topic.lower()
      if topic not in quotes_by_topic:
        quotes_by_topic[topic] = []
    quotes_by_topic[topic].append(quote_object)
    if author not in bio_by_author:
      bio_by_author[author] = bio

# Returns a quote object matching the parameters of the request.
def _get_quote():
    print(request.json)
    parameters = request.json['result']['parameters']
    author = None
    topic = None
    if 'author' in parameters:
      author = unicodedata.normalize('NFKC', parameters['author']).lower()
    if 'topic' in parameters:
      topic = unicodedata.normalize('NFKC', parameters['topic']).lower()

    applicable_author_quotes = set()
    if author:
      if author in quotes_by_author:
        applicable_author_quotes = set(quotes_by_author[author])
    else:
      applicable_author_quotes = set(quotes)

    applicable_topic_quotes = set()
    if topic:
      if topic in quotes_by_topic:
        applicable_topic_quotes = set(quotes_by_topic[topic])
    else:
      applicable_topic_quotes = set(quotes)

    applicable_quotes = applicable_author_quotes.intersection(applicable_topic_quotes)

    if len(applicable_quotes) == 0:
      return None

    quote_to_return = random.choice(tuple(applicable_quotes))

    return quote_to_return

def _get_bio():
    parameters = request.json['result']['parameters']
    if 'author' in parameters:
      author = unicodedata.normalize('NFKC', parameters['author']).lower()
      return bio_by_author.get(author)  # returns None if key does not exist
    else:
      return None

class QuoteSearch(Resource):
  def post(self):
    action = request.json['result']['action']

    if action == 'get_quote_event':
      quote = _get_quote()
      if quote:
        response_json = json.dumps({
          'followupEvent': {
              'name': 'respond_with_quote',
              'data': {
                  'quote': quote[0],
                  'author': quote[1]
              }
          }})
      else:
        response_json = json.dumps({
          'followupEvent': {
              'name': 'respond_with_quote',
              'data': {}
          }})

    elif action == 'get_quote_response':
      quote = _get_quote()
      if quote:
        response = 'Here is a quote by ' + quote[1] + ': ' + quote[0]
      else:
        response = 'I have no matching quote.'
      response_json = json.dumps({'speech': response, 'displayText': response})

    elif action == 'get_bio_event':
      bio = _get_bio()
      if bio:
        response_json = json.dumps({
          'followupEvent': {
              'name': 'respond_with_bio',
              'data': {
                  'bio': bio
              }
          }})
      else:
        response_json = json.dumps({
          'followupEvent': {
              'name': 'respond_with_bio',
              'data': {}
          }})

    elif action == 'get_bio_response':
      bio = _get_bio()
      if bio:
        response = 'Here is the bio: ' + bio
      else:
        response = 'I have no matching bio.'
      response_json = json.dumps({'speech': response, 'displayText': response})

    r = make_response(response_json)
    r.headers['Content-Type'] = 'application/json'
    return r

api.add_resource(QuoteSearch, '/quotesearch')

if __name__ == '__main__':
  app.run(debug=True)

# [END app]
