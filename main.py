# This app serves quotes from famous women in STEM by author and topic, and
# serves bios by author.
# Created for the "Building a Conversational Agent" workshop at the 2017
# Grace Hopper Conference.

import csv
import logging
import random
import unicodedata
from collections import namedtuple

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

# Dialogflow request and response field names.
RESULT_FIELD_V1 = 'result'
RESULT_FIELD_V2 = 'queryResult'
ACTION_FIELD = 'action'
PARAMS_FIELD = 'parameters'
AUTHOR_PARAM_NAME = 'author'
TOPIC_PARAM_NAME = 'topic'

EVENT_FIELD_V1 = 'followupEvent'
EVENT_FIELD_V2 = 'followupEventInput'
EVENT_NAME_FIELD = 'name'
EVENT_PARAMS_FIELD_V1 = 'data'
EVENT_PARAMS_FIELD_V2 = 'parameters'


app = Flask(__name__)
api = Api(app)

# Named tuple to store the relevant parameters of the request.
Params = namedtuple('Params', ['action', 'author', 'topic'])

# List of (quote, author, (topic1, topic2, ...)) tuples.
quotes = []

# Map from author string to list of quote objects.
quotes_by_author = {}

# Map from topic string to list of quote objects.
quotes_by_topic = {}

# Map from author string to bio string.
bio_by_author = {}

# Read in quotes and bios.
with open('quotes.csv', 'rb') as quotes_file:
  quotes_reader = csv.reader(quotes_file)

  # Skip the header line.
  next(quotes_reader, None)

  # Each line of the csv has the format
  # "quote, author, year_born, year_died, bio, date_spoken, source, topics,
  # comments".
  for row in quotes_reader:
    quote = row[0]
    author = row[1]
    bio = row[4]
    topics = tuple(x.lower().strip() for x in row[7].split(','))
    quote_object = (quote, author, topics)
    quotes.append(quote_object)
    normalized_author = author.lower()
    if normalized_author not in quotes_by_author:
      quotes_by_author[normalized_author] = []
    quotes_by_author[normalized_author].append(quote_object)
    for topic in list(topics):
      if topic not in quotes_by_topic:
        quotes_by_topic[topic] = []
      quotes_by_topic[topic].append(quote_object)
    if normalized_author not in bio_by_author:
      bio_by_author[normalized_author] = bio

# Exception for a bad request from the client.
class BadRequestError(ValueError):
  pass

# Returns a quote object matching the parameters of the request, or None if
# there are no matching quotes.
def _get_quote(params):
  # Find the set of quotes by the given author (all quotes if not specified).
  applicable_author_quotes = set()
  if params.author is None:
    applicable_author_quotes = set(quotes)
  else:
    if params.author in quotes_by_author:
      applicable_author_quotes = set(quotes_by_author[params.author])

  # Find the set of quotes on the given topic (all quotes if not given).
  applicable_topic_quotes = set()
  if params.topic is None:
    applicable_topic_quotes = set(quotes)
  else:
    if params.topic in quotes_by_topic:
      applicable_topic_quotes = set(quotes_by_topic[params.topic])

  # The matching quotes are in the intersection of the two sets.
  applicable_quotes = applicable_author_quotes.intersection(applicable_topic_quotes)

  # Return None if there are no matching quotes.
  if len(applicable_quotes) == 0:
    return None

  # Return one of the matching quotes randomly.
  quote_to_return = random.choice(tuple(applicable_quotes))

  return quote_to_return

# Returns the bio of the author specified in the parameters as a string, or
# None if there is no matching author.
def _get_bio(params):
  # Extract the author parameter. For robustness, the parameter name can be
  # capitalized in any way.
  if params.author is None:
    raise BadRequestError('No author parameter provided in request for a ' +
                          'bio, but an author must be specified.')

  return bio_by_author.get(params.author)  # returns None if key does not exist

# Returns a Params object populated with the parameters extracted from the
# result in the Dialogflow request.
def _extract_params(result):
  action = None
  author = None
  topic = None

  if ACTION_FIELD in result:
    action = result[ACTION_FIELD]

  # Extract the author and topic parameters, if present. For robustness, the
  # parameter names can be capitalized in any way.
  if PARAMS_FIELD in result:
    parameters_dict = result[PARAMS_FIELD]
    if parameters_dict:
      for key, value in parameters_dict.items():
        if key.lower() == AUTHOR_PARAM_NAME:
          if value:
            author = unicodedata.normalize('NFKC', value).lower()
        elif key.lower() == TOPIC_PARAM_NAME:
          if value:
            topic = unicodedata.normalize('NFKC', value).lower()
        else:
          raise BadRequestError('Unrecognized parameter in request: ' + key)

  return Params(action, author, topic)

# Returns an event response with the provided name and params.
def _get_response_event(name, params, is_v1):
  if is_v1:
    event_field = EVENT_FIELD_V1
    params_field = EVENT_PARAMS_FIELD_V1
  else:
    event_field = EVENT_FIELD_V2
    params_field = EVENT_PARAMS_FIELD_V2
  return {
           event_field : {
             EVENT_NAME_FIELD : name,
             params_field : params
           }
         }

# Returns a text response with the provided text.
def _get_response_text(text, is_v1):
  if is_v1:
    return {'speech': text, 'displayText': text}
  else:
    return {'fulfillmentText': text}


class QuoteSearch(Resource):
  # Handles a request from API.AI. The relevant part of the body is:
  # {
  #   "result": {
  #       "parameters": {
  #           <key>: <value>,
  #           <key>: <value>
  #       },
  #       "action": <action>
  #   }
  # }
  # See the README for the full API, and for a full sample request see
  # https://dialogflow.com/docs/fulfillment#request.
  def post(self):
    try:
      if not request.json:
        raise BadRequestError('No json body was provided in the request.')

      if RESULT_FIELD_V1 in request.json:
        params = _extract_params(request.json[RESULT_FIELD_V1])
        is_v1 = True
      elif RESULT_FIELD_V2 in request.json:
        params = _extract_params(request.json[RESULT_FIELD_V2])
        is_v1 = False
      else:
        raise BadRequestError('Neither "result" nor "queryResult" was ' +
                              'provided in the request body.')

      if params.action is None:
        raise BadRequestError('No "action" was provided in the request.')

      if params.action == 'get_quote_event':
        quote = _get_quote(params)
        if quote:
          response_body = _get_response_event(
            'respond_with_quote', 
            {
              'quote': quote[0],
              'author': quote[1]
            },
            is_v1)
        else:
          response_body = _get_response_event('quote_not_found', {}, is_v1)

      elif params.action == 'get_quote_response':
        quote = _get_quote(params)
        if quote:
          response = 'Here is a quote by ' + quote[1] + ': ' + quote[0]
        else:
          response = 'I have no matching quote.'
        response_body = _get_response_text(response, is_v1)

      elif params.action == 'get_bio_event':
        bio = _get_bio(params)
        if bio:
          response_body = _get_response_event(
            'respond_with_bio',
            {
              'bio': bio
            },
            is_v1)
        else:
          response_body = _get_response_event('bio_not_found', {}, is_v1)

      elif params.action == 'get_bio_response':
        bio = _get_bio(params)
        if bio:
          response = 'Here is the bio: ' + bio
        else:
          response = 'I have no matching bio.'
        response_body = _get_response_text(response, is_v1)

      else:
        raise BadRequestError('Request action unrecognized: "' +
                              params.action + '"')

      return jsonify(response_body)

    except BadRequestError as error:
      response = jsonify(status=400, message=error.message)
      response.status_code = 400
      return response

# Register the quotesearch endpoint to be handled by the QuoteSerch class.
api.add_resource(QuoteSearch, '/quotesearch')

if __name__ == '__main__':
  app.run()

