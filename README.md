This is a service to serve quotes and bios of famous women in STEM.
It is used as the webhook for a demo conversational agent built with
[API.AI](https://api.ai/) for the "Building a Conversational Agent" workshop
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

    curl -X POST http://localhost:8080/quotesearch -H "Content-Type: application/json" -d '{"result": {"action": "get_quote_event", "parameters": {"author": "Grace Hopper", "topic": "technology"}}}' 

Example response:

    {"followupEvent": {"data": {"author": "Grace Hopper", "quote": "The application of systems techniques has been successful in scientific and technical applications . . . It meets difficulty when it is applied in social and political situations largely because people are not 'well-behaved' mathematical functions, but can only be represented by statistical approximations, and all of the extremes can and do occur."}, "name": "respond_with_quote"}}

To deploy, run

    gcloud app deploy app.yaml

The service has one endpoint '/quotesearch'. It accepts POST requests with
Content-type application/json as sent by API.AI. See the full request format
[here](https://api.ai/docs/fulfillment#request). It handles 4 actions:

<table>
  <tbody>
    <tr>
      <td>Objective</td>
      <td>Body</td>
      <td>Output</td>
    </tr>
    <tr>
      <td>
        <div>Get a quote response as a followup event.</div>
      </td>
      <td>
        <div>{<br>  …<br>  &quot;result&quot;: {<br>    &quot;parameters&quot;: {<br>      &quot;author&quot;: &quot;Grace Hopper&quot;,<br>      &quot;topic&quot;: &quot;computers&quot;<br>    }, <br>    &quot;action&quot;: &quot;get_quote_event&quot;<br>    …<br>  }<br>}<br><br>Both parameters are optional.</div>
      </td>
      <td>
        <div>{<br>  &quot;followupEvent&quot;: {<br>    &quot;name&quot;: &quot;respond_with_quote&quot;,   <br>    &quot;data&quot;: {<br>      &quot;quote&quot;:&quot;computers&quot;,   <br>      "author":"Grace Hopper"<br>    }<br>  }<br>}<br><br>|data| will be empty if there is no applicable quote.</div>
      </td>
    </tr>
    <tr>
      <td>
        <div>Get a quote response as response text.</div>
      </td>
      <td>
        Same as above, except<br><br>&quot;action&quot;: &quot;get_quote_response&quot;
      </td>
      <td>
        <div>{<br>  "displayText": "Here’s a quote by Grace Hopper: computers",<br>  "speech": "Here’s a quote by Grace Hopper: computers"<br>}</div>
      </td>
    </tr>
    <tr>
      <td>
        <div>Get an author bio response as a followup event.</div>
      </td>
      <td>
        <div>{<br>  …<br>  &quot;result&quot;: {<br>    &quot;parameters&quot;: {<br>      &quot;author&quot;: &quot;Grace Hopper&quot;<br>    }, <br>    &quot;action&quot;: &quot;get_bio_event&quot;<br>    …<br>  }<br>}<br><br>The |author| parameter is required.</div>
      </td>
      <td>
        <div>{<br>  &quot;followupEvent&quot;: {<br>    &quot;name&quot;: &quot;respond_with_bio&quot;,   <br>    &quot;data&quot;: {<br>      &quot;bio&quot;:&quot;Grace Hopper was a computer scientist.&quot;<br>    }<br>  }<br>}<br><br>|data| will be empty if there is no matching bio.</div>
      </td>
    </tr>
    <tr>
      <td>
        <div>Get an author bio response as response text.</div>
      </td>
      <td>
        Same as above, except<br><br>&quot;action&quot;: &quot;get_bio_response&quot;
      </td>
      <td>
        <div>{<br>  "displayText": "Here’s the bio of Grace Hopper: Grace Hopper was a computer scientist.",<br>  "speech": "Here’s the bio of Grace Hopper: Grace Hopper was a computer scientist."<br>}</div>
      </td>
    </tr>
  </tbody>
</table>
