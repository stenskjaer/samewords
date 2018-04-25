.. _apiinterface:

API Interface
=============

There is an API endpoint for the web service (UI available at
https://s3.amazonaws.com/samewords-app/index.html).

Endpoint: https://90tqezjfmk.execute-api.us-east-1.amazonaws.com/prod

Query parameters:

- url: the absolute url of the file that you want processed.
- mode: the processing mode that you want to apply. Options are ["annotate",
  "update", "clean"]

An example call would therefore be to
``https://90tqezjfmk.execute-api.us-east-1.amazonaws.com/prod?url=https://myamazingserver.net/my-edition.tex?mode=update``.
