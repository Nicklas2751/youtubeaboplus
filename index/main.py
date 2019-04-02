# -*- coding: utf-8 -*-

import os

import flask

import googleapiclient.discovery
import google.oauth2.credentials
from googleapiclient.errors import HttpError
from flask import current_app as app
app.secret_key = os.environ['FLASK_SECRET_KEY']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def index(request):  
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
  # Build the Google API client
  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, cache_discovery=False, credentials=credentials)
  
  return addAllSince(request,client)

# Adds all videos since the video with the given HTTP GET argument lastVideoId was published to the watch later playlist.
def addAllSince(request,client):
    lastVideoId=request.args.get('lastVideoId')
    playlistId="WL"
    # Check if the lasVideoId argument is set and if the playlistId isn't empty.
    if 'lastVideoId' in request.args and playlistId is not "" :
      # Gather the published at date for the video with the given ID.
      lastVideoTime=getPublishedAtLastVideo(client,lastVideoId)
      if lastVideoTime is not "":
        # Gather all IDs of the subscribed channels.
        subscribedChannels = subscriptionsToSubscribedChannels(mine_subscriptions(client))
        # Gather all uploads for all subscribed channels and sort them by their published at date.
        uploads = orderUploads(gatherUploadsForSubscribedChannels(client,lastVideoTime,subscribedChannels))
        # Add all these uploads to the watch later playlist.
        addUploadsToPlaylist(client,playlistId,uploads)
        return "Added %d Videos to watch later." % (len(uploads))
    return "Something was missing. Added no Videos to watch later."

# Calls the API for each upload and add it to the playlist with the given ID.
def addUploadsToPlaylist(client,playlistId,uploads):
  for upload in uploads:
    try:
      client.playlistItems().insert(body={"snippet": { "playlistId": playlistId, "resourceId": { "videoId": upload.videoId, "kind": "youtube#video" }}},part='snippet').execute()
    except HttpError as e:
      print("The video with the ID {} couldn't be added because of an HTTP error {}.".format(upload.videoId, e))

# Order the uploads by theiry published at date
def orderUploads(uploads):
    return sorted(uploads, key=lambda upload: upload.publishedAt, reverse=False)
    
# Gather all uploads for all subscribed channels
def gatherUploadsForSubscribedChannels(client,lastVideoTime,subscribedChannels):
  uploads = []
  for subscribedChannel in subscribedChannels:
    # Extend the uploads with the uploads for the specific channel
    uploads.extend(getChannelUploadsSince(client,subscribedChannel,lastVideoTime))
  
  return uploads

# Gather all uploads for a channel since the given time.
def getChannelUploadsSince(client,channelId,time):
  # All activities for the channel page 1
  activities = client.activities().list(part='snippet,contentDetails', channelId=channelId, maxResults=50, publishedAfter=time,fields='items(contentDetails/upload,snippet(title,type,publishedAt)),nextPageToken').execute()
  activityItems = []
  activityItems.extend(activities['items'])
  # Do while a next page token comes back
  while 'nextPageToken' in activities:
    activities = client.activities().list(part='snippet,contentDetails', pageToken=activities['nextPageToken'], channelId=channelId, maxResults=50, publishedAfter=time,fields='items(contentDetails/upload,snippet(title,type,publishedAt)),nextPageToken').execute()
    activityItems.extend(activities['items'])
  print("Found %d activities!" % (len(activityItems))) 

  uploads = []
  # Convert all activities with the type "upload" to a video upload object.
  for activity in activityItems:
    if activity['snippet']['type'] == 'upload':
      uploads.append(VideoUpload(activity['contentDetails']['upload']['videoId'],activity['snippet']['publishedAt']))
  
  return uploads

# Convert all subscriptions to their channel IDs.
def subscriptionsToSubscribedChannels(subscriptions):
  subscribedChannels = []
  for subscription in subscriptions:
      subscribedChannels.append(subscription['snippet']['resourceId']['channelId'])
  
  return subscribedChannels

# Gather the published at date for the video with the given id.
def getPublishedAtLastVideo(client,lastVideoId):
  response = client.videos().list(part='snippet', id=lastVideoId,fields='items/snippet/publishedAt').execute()
  responseItems = response['items']
  if len(responseItems) >= 1:
    for responseItem in responseItems:
      return responseItem['snippet']['publishedAt']
  return ""
    
# Get all subscriptions for the user    
def mine_subscriptions(client):
  subscriptionItems = []
  subscriptions = client.subscriptions().list(part='snippet', maxResults=50,mine="true",fields='items/snippet/resourceId/channelId,nextPageToken').execute()
  subscriptionItems.extend(subscriptions['items'])
  while 'nextPageToken' in subscriptions:
        subscriptions = client.subscriptions().list(part='snippet', pageToken=subscriptions['nextPageToken'], maxResults=50,mine="true",fields='items/snippet/resourceId/channelId,nextPageToken').execute()
        subscriptionItems.extend(subscriptions['items'])
  
  return subscriptionItems

# A class to store the video id and the published at data for a single upload/video.
class VideoUpload:
  def __init__(self, videoId, publishedAt):
    self.videoId = videoId
    self.publishedAt = publishedAt
