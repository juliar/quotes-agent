"""
Tests for main.py.
"""

import json
import main
import unittest

class MainTestCase(unittest.TestCase):

  def setUp(self):
    main.app.testing = True
    self.app = main.app.test_client()

  def _do_request(self, data):
    return self.app.post('/quotesearch', content_type='application/json',
                         data=json.dumps(data))

  def _do_request_with_inputs(self, action, parameters):
    return self._do_request({
        'result': {
            'parameters': parameters,
            'action': action
        }
    })

  # Performs a request to get a pre-defined response with the given action and
  # parameters, and returns the response string, checking that the response
  # displayText and speech response are the same.
  def _get_response_text(self, action, parameters):
    response = self._do_request_with_inputs(action, parameters)
    message = json.loads(response.data)
    response_text = message['displayText']
    response_speech = message['speech']
    assert response_text == response_speech
    return response_text

  # Performs a request to get an event with the given action and parameters,
  # and returns the name and data for the event.
  def _get_response_event(self, action, parameters):
    response = self._do_request_with_inputs(action, parameters)
    message = json.loads(response.data)
    name = message['followupEvent']['name']
    data = message['followupEvent']['data']
    return name, data


  """ Tests for bad requests """

  def _test_bad_request(self, response, expected_message):
    self.assertEqual('400 BAD REQUEST', response.status)
    data = json.loads(response.data)
    self.assertEqual(expected_message, data['message'])

  def test_no_json_body(self):
    response = self.app.post('/quotesearch')
    self._test_bad_request(response,
                           'No json body was provided in the request.')

  def test_result_not_in_request(self):
    response = self._do_request({'irrelevant': 'doesnt matter'})
    self._test_bad_request(response,
                           '"result" was not provided in the request body.')

  def test_no_action_provided(self):
    response = self._do_request({'result': {}})
    self._test_bad_request(response,
                           'No "action" was provided in the request.')

  def test_unrecognized_action(self):
    response = self._do_request({'result': {'action': 'make_some_tea'}})
    self._test_bad_request(response,
                           'Request action unrecognized: "make_some_tea"')


  """ Tests for action get_quote_response """

  def test_get_quote_response(self):
    response_text = self._get_response_text('get_quote_response', {})
    assert 'Here is a quote by' in response_text

  def test_get_quote_response_by_author(self):
    response_text = self._get_response_text(
        'get_quote_response',
        {'author': 'Grace Hopper'})
    assert 'Here is a quote by Grace Hopper' in response_text

  def test_get_quote_response_by_topic(self):
    response_text = self._get_response_text(
        'get_quote_response',
        {'topic': 'mathematics'})
    assert 'Here is a quote by' in response_text
    assert 'math' in response_text.lower()

  def test_get_quote_response_by_author_and_topic(self):
    response_text = self._get_response_text(
        'get_quote_response',
        {'author': 'Grace Hopper',
         'topic': 'mathematics'})
    assert 'Here is a quote by Grace Hopper' in response_text
    assert 'math' in response_text.lower()

  def test_get_quote_response_parameter_capitalization(self):
    response_text = self._get_response_text(
        'get_quote_response',
        {'auThOr': 'grace hOpPer',
         'tOPIc': 'mAthEmatIcs'})
    assert 'Here is a quote by Grace Hopper' in response_text
    assert 'math' in response_text.lower()

  def test_get_quote_response_no_match(self):
    response_text = self._get_response_text(
        'get_quote_response',
        {'author': 'ksdjdkj'})
    assert response_text == 'I have no matching quote.'

  def test_get_quote_response_unrecognized_parameter(self):
    response = self._do_request_with_inputs('get_quote_response',
                                            {'diameter': 4})
    self._test_bad_request(response,
                           'Unrecognized parameter in request: diameter')


  """ Tests for action get_quote_event """

  def test_get_quote_event(self):
    name, data = self._get_response_event('get_quote_event', {})
    assert name == 'respond_with_quote'
    assert data['quote']
    assert data['author']

  def test_get_quote_event_by_author(self):
    name, data = self._get_response_event(
        'get_quote_event',
        {'author': 'Grace Hopper'})
    assert name == 'respond_with_quote'
    assert data['quote']
    assert data['author'] == 'Grace Hopper'

  def test_get_quote_event_by_topic(self):
    name, data = self._get_response_event(
        'get_quote_event',
        {'topic': 'mathematics'})
    assert name == 'respond_with_quote'
    assert 'math' in data['quote'].lower()
    assert data['author']

  def test_get_quote_event_by_author_and_topic(self):
    name, data = self._get_response_event(
        'get_quote_event',
        {'author': 'Grace Hopper',
         'topic': 'mathematics'})
    assert name == 'respond_with_quote'
    assert 'math' in data['quote'].lower()
    assert data['author'] == 'Grace Hopper'

  def test_get_quote_event_parameter_capitalization(self):
    name, data = self._get_response_event(
        'get_quote_event',
        {'auThOr': 'grace hOpPer',
         'tOPIc': 'mAthEmatIcs'})
    assert name == 'respond_with_quote'
    assert 'math' in data['quote'].lower()
    assert data['author'] == 'Grace Hopper'

  def test_get_quote_event_no_match(self):
    name, data = self._get_response_event(
        'get_quote_event',
        {'author': 'asdfjkjhd'})
    assert name == 'respond_with_quote'
    assert 'quote' not in data
    assert 'author' not in data

  def test_get_quote_event_unrecognized_parameter(self):
    response = self._do_request_with_inputs('get_quote_event', {'diameter': 4})
    self._test_bad_request(response,
                           'Unrecognized parameter in request: diameter')

  """ Tests for action get_bio_response """

  def test_get_bio_response(self):
    response_text = self._get_response_text(
        'get_bio_response',
        {'author': 'Grace Hopper'})
    assert 'computer scientist' in response_text.lower()

  def test_get_bio_response_parameter_capitalization(self):
    response_text = self._get_response_text(
        'get_bio_response',
        {'auThOr': 'grace hOpPer'})
    assert 'computer scientist' in response_text.lower()

  def test_get_bio_response_no_match(self):
    response_text = self._get_response_text(
        'get_bio_response',
        {'author': 'asdkfjasdf'})
    assert response_text == 'I have no matching bio.'

  def test_get_bio_response_unrecognized_parameter(self):
    response = self._do_request_with_inputs('get_bio_response',
                                            {'author': 'Grace Hopper',
                                             'diameter': 4})
    self._test_bad_request(response,
                           'Unrecognized parameter in request: diameter')

  def test_get_bio_response_missing_author_parameter(self):
    response = self._do_request_with_inputs('get_bio_response', {})
    self._test_bad_request(response,
                           'No author parameter provided in request for bio.')


  """ Tests for action get_bio_event """

  def test_get_bio_event(self):
    name, data = self._get_response_event(
        'get_bio_event',
        {'author': 'Grace Hopper'})
    assert name == 'respond_with_bio'
    assert 'computer scientist' in data['bio'].lower()

  def test_get_bio_event_parameter_capitalization(self):
    name, data = self._get_response_event(
        'get_bio_event',
        {'auThOr': 'grace hOpPer'})
    assert name == 'respond_with_bio'
    assert 'computer scientist' in data['bio'].lower()

  def test_get_bio_event_no_match(self):
    name, data = self._get_response_event(
        'get_bio_event',
        {'author': 'asdkjfaksjdhf'})
    assert name == 'respond_with_bio'
    assert 'bio' not in data

  def test_get_bio_event_unrecognized_parameter(self):
    response = self._do_request_with_inputs('get_bio_event',
                                            {'author': 'Grace Hopper',
                                             'diameter': 4})
    self._test_bad_request(response,
                           'Unrecognized parameter in request: diameter')

  def test_get_bio_event_missing_author_parameter(self):
    response = self._do_request_with_inputs('get_bio_event', {})
    self._test_bad_request(response,
                           'No author parameter provided in request for bio.')


if __name__ == '__main__':
  unittest.main()
