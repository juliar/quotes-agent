This is a service to serve quotes and bios of famous women in STEM.
It is used as the webhook for a demo conversational agent built with
[Dialogflow](http://dialogflow.com/) for the "Building a Conversational Agent" workshop
at the 2017 Grace Hopper Conference.

The service is written using [Flask-RESTful](https://flask-restful.readthedocs.io)
and deployed using [App Engine](http://cloud.google.com/appengine/docs/) on
[Google Cloud Platform](https://cloud.google.com/).

Before running or deploying, install the dependencies using
[pip](http://pip.readthedocs.io):

    pip install -t lib -r requirements.txt

To run the service locally, you can run

    dev_appserver.py .

Then you can test an example request:

    curl -X POST http://localhost:8080/quotesearch -H "Content-Type: application/json" -d '{"queryResult": {"action": "get_quote_event", "parameters": {"author": "Grace Hopper", "topic": "technology"}}}' 

Example response:

    {"followupEventInput": {"parameters": {"author": "Grace Hopper", "quote": "The application of systems techniques has been successful in scientific and technical applications . . . It meets difficulty when it is applied in social and political situations largely because people are not 'well-behaved' mathematical functions, but can only be represented by statistical approximations, and all of the extremes can and do occur."}, "name": "respond_with_quote"}}

To deploy, run

    gcloud app deploy app.yaml

The service has one endpoint '/quotesearch'. It accepts POST requests with
Content-type application/json as sent by Dialogflow. See the full request format
[here](https://dialogflow.com/docs/fulfillment#request). It handles 4 actions:

<table>
  <tbody>
    <tr>
      <th width="20%">Action</td>
      <th width="40%">Body</td>
      <th width="40%">Output</td>
    </tr>
    <tr>
      <td>
        <div>get_quote_event<br><br>Get a quote response as a followup event.</div>
      </td>
      <td>
        <div>{<br>&emsp;…<br>&emsp;&quot;queryResult&quot;: {<br>&emsp;&emsp;&quot;parameters&quot;: {<br>&emsp;&emsp;&emsp;&quot;author&quot;: &quot;Grace Hopper&quot;,<br>&emsp;&emsp;&emsp;&quot;topic&quot;: &quot;computers&quot;<br>&emsp;&emsp;}, <br>&emsp;&emsp;&quot;action&quot;: &quot;get_quote_event&quot;<br>&emsp;&emsp;…<br>&emsp;}<br>}<br><br>Both parameters are optional.</div>
      </td>
      <td>
        <div>{<br>&emsp;&quot;followupEventInput&quot;: {<br>&emsp;&emsp;&quot;name&quot;: &quot;respond_with_quote&quot;,&emsp;&emsp;<br>&emsp;&emsp;&quot;parameters&quot;: {<br>&emsp;&emsp;&emsp;&quot;quote&quot;: &quot;computers&quot;,   <br>&emsp;&emsp;&emsp;"author": "Grace Hopper"<br>&emsp;&emsp;}<br>&emsp;}<br>}<br><br>If there is no applicable quote, |name| will be "quote_not_found" instead.</div>
      </td>
    </tr>
    <tr>
      <td>
        <div>get_quote_response<br><br>Get a quote response as response text.</div>
      </td>
      <td>
        Same as above, except<br><br>&quot;action&quot;: &quot;get_quote_response&quot;
      </td>
      <td>
        <div>{<br>&emsp;"fulfillmentText": "Here’s a quote..."<br>}</div>
      </td>
    </tr>
    <tr>
      <td>
        <div>get_bio_event<br><br>Get an author bio response as a followup event.</div>
      </td>
      <td>
        <div>{<br>&emsp;…<br>&emsp;&quot;queryResult&quot;: {<br>&emsp;&emsp;&quot;parameters&quot;: {<br>&emsp;&emsp;&emsp;&quot;author&quot;: &quot;Grace Hopper&quot;<br>&emsp;&emsp;}, <br>&emsp;&emsp;&quot;action&quot;: &quot;get_bio_event&quot;<br>&emsp;&emsp;…<br>&emsp;}<br>}<br><br>The |author| parameter is required.</div>
      </td>
      <td>
        <div>{<br>  &quot;followupEventInput&quot;: {<br>&emsp;&emsp;&quot;name&quot;: &quot;respond_with_bio&quot;,&emsp;&emsp;<br>&emsp;&emsp;&quot;parameters&quot;: {<br>&emsp;&emsp;&emsp;&quot;bio&quot;: &quot;Grace Hopper...&quot;<br>&emsp;&emsp;}<br>&emsp;}<br>}<br><br>If there is no matching bio, |name| will be "bio_not_found" instead.</div>
      </td>
    </tr>
    <tr>
      <td>
        <div>get_bio_response<br><br>Get an author bio response as response text.</div>
      </td>
      <td>
        Same as above, except<br><br>&quot;action&quot;: &quot;get_bio_response&quot;
      </td>
      <td>
        <div>{<br>&emsp;"fulfillmentText": "Here’s the bio..."<br>}</div>
      </td>
    </tr>
  </tbody>
</table>
