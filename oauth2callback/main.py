# -*- coding: utf-8 -*-

import os
import flask
import logging
import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask import current_app as app
app.secret_key = os.environ['FLASK_SECRET_KEY']

SCOPES = ['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl','https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtubepartner','https://www.googleapis.com/auth/youtubepartner-channel-audit','https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile']

def oauth2callback(request):
  # Specify the state when creating the flow in the callback so that it can
  # verify the authorization server response.
  state = flask.session['state']
  flow = google_auth_oauthlib.flow.Flow.from_client_config({
 		 "web": {
    		"client_id": os.environ['OAUTH_CLIENT_ID'],
            "project_id": os.environ['OAUTH_PROJECT_ID'],
            "auth_uri": os.environ['OAUTH_AUTH_URI'],
            "token_uri": os.environ['OAUTH_TOKEN_URI'],
            "auth_provider_x509_cert_url": os.environ['OAUTH_AUTH_PROVIDER_CERT_URL'],
    		"client_secret": os.environ['OAUTH_CLIENT_SECRET'],
    		"redirect_uris": [os.environ['OAUTH_REDIRCET_URIS']]    		
  			}
		},
       scopes=SCOPES)
  flow.redirect_uri = os.environ['OAUTH_REDIRCET_URIS']
  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  flow.fetch_token(authorization_response=flask.request.url.replace('http', 'https'))

  # Store the credentials in the session.
  # ACTION ITEM for developers:
  #     Store user's access and refresh tokens in your data store if
  #     incorporating this code into your real app.
  credentials = flow.credentials
  flask.session['credentials'] = {'token': credentials.token,
				  'refresh_token': credentials.refresh_token,
                                  'token_uri': credentials.token_uri,
                                  'client_id': credentials.client_id,
                                  'client_secret': credentials.client_secret,
                                  'scopes': credentials.scopes}

  return flask.redirect(os.environ['INDEX_URI'])
