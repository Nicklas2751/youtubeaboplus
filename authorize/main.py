# -*- coding: utf-8 -*-

import os

import flask

import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask import current_app as app
app.secret_key = os.environ['FLASK_SECRET_KEY']

SCOPES = ['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl','https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtubepartner','https://www.googleapis.com/auth/youtubepartner-channel-audit','https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile']

def authorize(request):
  # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
  # steps.
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
  authorization_url, state = flow.authorization_url(
      # This parameter enables offline access which gives your application
      # both an access and refresh token.
      access_type='offline',
      # This parameter enables incremental auth.
      include_granted_scopes='true')

  # Store the state in the session so that the callback can verify that
  # the authorization server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)