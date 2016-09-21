import sqlite3
import sys
import argparse
import os
import json
import operator
import shutil
import smtplib
import requests
import base64
import cloudinary
import cloudinary.uploader
import cloudinary.api
import imghdr
import time
import logging
import traceback
from base64 import b64encode
from collections import OrderedDict
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage
from email.header import Header
from email.utils import formataddr
from xml.etree.ElementTree import XML

SCRIPT_VERSION = 'v0.9.1'

def replaceConfigTokens():
  ## The below code is for backwards compatibility
  if ('logging_enabled' not in config):
    config['logging_enabled'] = True
    
  if ('plex_web_server_guid' not in config):
    config['plex_web_server_guid'] = ''
    
  if ('upload_cloudinary_use_https' not in config):
    config['upload_cloudinary_use_https'] = True
  
  if ('logging_retain_previous_logs' not in config):
    config['logging_retain_previous_logs'] = True
    
  if ('logging_debug_level' not in config):
    config['logging_debug_level'] = 'INFO'
    
  if ('logging_file_location' not in config):
    config['logging_file_location'] = ''
  
  if ('upload_cloudinary_api_secret' not in config):
    config['upload_cloudinary_api_secret'] = True
    
  if ('artist_sort_1' not in config.keys() or config['artist_sort_1'] == ""):
    config['artist_sort_1'] = 'title_sort'
    
  if ('artist_sort_1_reverse' not in config.keys() or config['artist_sort_1_reverse'] == ""):
    config['artist_sort_1_reverse'] = False
  if ('artist_sort_2_reverse' not in config.keys() or config['artist_sort_2_reverse'] == ""):
    config['artist_sort_2_reverse'] = False
  if ('artist_sort_3_reverse' not in config.keys() or config['artist_sort_3_reverse'] == ""):
    config['artist_sort_3_reverse'] = False
    
  if ('album_sort_1' not in config.keys() or config['album_sort_1'] == ""):
    config['album_sort_1'] = 'title_sort'
    
  if ('album_sort_1_reverse' not in config.keys() or config['album_sort_1_reverse'] == ""):
    config['album_sort_1_reverse'] = False
  if ('album_sort_2_reverse' not in config.keys() or config['album_sort_2_reverse'] == ""):
    config['album_sort_2_reverse'] = False
  if ('album_sort_3_reverse' not in config.keys() or config['album_sort_3_reverse'] == ""):
    config['album_sort_3_reverse'] = False
    
  if ('msg_new_artists_header' not in config):
    config['msg_new_artists_header'] = 'New Artists'
    
  if ('msg_new_albums_header' not in config):
    config['msg_new_albums_header'] = 'New Albums'
    
  if ('msg_new_songs_header' not in config):
    config['msg_new_songs_header'] = 'New Songs'
    
  if ('msg_artists_link' not in config):
    config['msg_artists_link'] = 'Artists'
    
  if ('msg_albums_link' not in config):
    config['msg_albums_link'] = 'Albums'
    
  if ('msg_songs_link' not in config):
    config['msg_songs_link'] = 'Songs'
    
  if ('filter_show_artists' not in config):
    config['filter_show_artists'] = True
    
  if ('filter_show_albums' not in config):
    config['filter_show_albums'] = True
    
  if ('filter_show_songs' not in config):
    config['filter_show_songs'] = False
    
  if ('filter_sections_Music' not in config):
    config['filter_sections_Music'] = {'tagline':{'order':1,'show':False,'preText':'<i>','postText':'</i>','include':[],'exclude':[]},'summary':{'order':2,'show':True,'preText':'','postText':'','include':[],'exclude':[]},'tags_genre':{'order':3,'show':True,'preText':'Genre(s): ','postText':'','include':[],'exclude':[]},'tags_director':{'order':4,'show':False,'preText':'Director: ','postText':'','include':[],'exclude':[]},'tags_star':{'order':5,'show':False,'preText':'Star(s): ','postText':'','include':[],'exclude':[]},'content_rating':{'order':6,'show':False,'preText':'ContentRating: ','postText':'','include':[],'exclude':[]},'duration':{'order':7,'show':True,'preText':'Runtime: ','postText':' minutes','include':[],'exclude':[]},'year':{'order':8,'show':False,'preText':'Year: ','postText':'','include':[],'exclude':[]},'studio':{'order':9,'show':True,'preText':'Network: ','postText':'','include':[],'exclude':[]},'rating':{'order':10,'show':False,'preText':'Rating: ','postText':'%','include':[],'exclude':[]},'air_date':{'order':11,'show': True,'preText':'Release Date: ','postText':'','include':[],'exclude':[],'format': '%B %d, %Y'},'track_list':{'order':12,'show': True,'headerText':{'trackNumber':'Track#','songName':'Song Name','artistName':'Artist(s)','duration':'Duration'}}}
    
  if ('filter_artists_include' not in config):
    config['filter_artists_include'] = []
    
  if ('filter_artists_exclude' not in config):
    config['filter_artists_exclude'] = []
    
  if ('filter_albums_include' not in config):
    config['filter_albums_include'] = []
    
  if ('filter_albums_exclude' not in config):
    config['filter_albums_exclude'] = []
    
  if ('filter_songs_include' not in config):
    config['filter_songs_include'] = []
    
  if ('filter_songs_exclude' not in config):
    config['filter_songs_exclude'] = []
    
  if ('filter_song_thumbnail_type' not in config):
    config['filter_song_thumbnail_type'] = 'album'
    
  if ('filter_movies_include' not in config):
    config['filter_movies_include'] = []
    
  if ('filter_movies_exclude' not in config):
    config['filter_movies_exclude'] = []
    
  if ('filter_shows_include' not in config):
    config['filter_shows_include'] = []
    
  if ('filter_shows_exclude' not in config):
    config['filter_shows_exclude'] = []
    
  if ('filter_seasons_include' not in config):
    config['filter_seasons_include'] = []
    
  if ('filter_seasons_exclude' not in config):
    config['filter_seasons_exclude'] = []
    
  if ('filter_episodes_include' not in config):
    config['filter_episodes_include'] = []
    
  if ('filter_episodes_exclude' not in config):
    config['filter_episodes_exclude'] = []
    
  if ('filter_episode_thumbnail_type' not in config):
    config['filter_episode_thumbnail_type'] = 'episode'
  
  if ('email_unsubscribe' not in config):
    config['email_unsubscribe'] = []
    
  if ('email_use_bcc' not in config):
    config['email_use_bcc'] = False
    
  if ('email_to_send_to_shared_users' not in config):
    config['email_to_send_to_shared_users'] = False
    
  if ('plex_username' not in config):
    config['plex_username'] = ''
    
  if ('plex_password' not in config):
    config['plex_password'] = ''
    
  if ('filter_show_email_images' not in config):
    config['filter_show_email_images'] = True
    
  if ('msg_notice' not in config):
    config['msg_notice'] = ''
  
  if ('email_use_ssl' not in config):
    config['email_use_ssl'] = False
    
  if ('filter_include_plex_web_link' not in config):
    config['filter_include_plex_web_link'] = True
    
  if ('filter_libraries' not in config):
    config['filter_libraries'] = []
  
  if ('filter_sections_movies' not in config):
    config['filter_include_sections_movies'] = {'tagline':{'order':1,'show':True,'preText':'<i>','postText':'</i>','include':[],'exclude':[]},'summary':{'order':2,'show':True,'preText':'','postText':'','include':[],'exclude':[]},'tags_genre':{'order':3,'show':True,'preText':'Genre(s): ','postText':'','include':[],'exclude':[]},'tags_director':{'order':4,'show':False,'preText':'Director: ','postText':'','include':[],'exclude':[]},'tags_star':{'order':5,'show':True,'preText':'Star(s): ','postText':'','include':[],'exclude':[]},'content_rating':{'order':6,'show':False,'preText':'ContentRating: ','postText':'','include':[],'exclude':[]},'duration':{'order':7,'show':True,'preText':'Runtime: ','postText':' minutes','include':[],'exclude':[]},'year':{'order':8,'show':True,'preText':'Year: ','postText':'','include':[],'exclude':[]},'studio':{'order':9,'show':False,'preText':'Studio: ','postText':'','include':[],'exclude':[]},'rating':{'order':10,'show':True,'preText':'Rating: ','postText':'%','include':[],'exclude':[]}}
  
  if ('filter_sections_TV' not in config):
    config['filter_include_sections_TV'] = {'tagline':{'order':1,'show':True,'preText':'<i>','postText':'</i>','include':[],'exclude':[]},'summary':{'order':2,'show':True,'preText':'','postText':'','include':[],'exclude':[]},'tags_genre':{'order':3,'show':False,'preText':'Genre(s): ','postText':'','include':[],'exclude':[]},'tags_director':{'order':4,'show':False,'preText':'Director: ','postText':'','include':[],'exclude':[]},'tags_star':{'order':5,'show':False,'preText':'Star(s): ','postText':'','include':[],'exclude':[]},'content_rating':{'order':6,'show':False,'preText':'ContentRating: ','postText':'','include':[],'exclude':[]},'duration':{'order':7,'show':True,'preText':'Runtime: ','postText':' minutes','include':[],'exclude':[]},'year':{'order':8,'show':False,'preText':'Year: ','postText':'','include':[],'exclude':[]},'studio':{'order':9,'show':True,'preText':'Network: ','postText':'','include':[],'exclude':[]},'rating':{'order':10,'show':False,'preText':'Rating: ','postText':'%','include':[],'exclude':[]}}
    
  if ('web_only_save_images' not in config):
    config['web_only_save_images'] = False
    
  if ('filter_show_movies' not in config):
    config['filter_show_movies'] = True
  
  if ('filter_show_shows' not in config):
    config['filter_show_shows'] = True
    
  if ('filter_show_seasons' not in config):
    config['filter_show_seasons'] = True
    
  if ('filter_show_episodes' not in config):
    config['filter_show_episodes'] = True
  
  if ('date_minutes_back_to_search' not in config):
    config['date_minutes_back_to_search'] = 0
  
  if ('msg_no_new_content' not in config):
    config['msg_no_new_content'] = 'There have been no new additions to Plex from {past_day} through {current_day}.'
    
  if ('email_skip_if_no_additions' not in config):
    config['email_skip_if_no_additions'] = False
  
  if ('web_skip_if_no_additions' not in config):
    config['web_skip_if_no_additions'] = False
    
  if ('date_days_back_to_search' not in config and 'days_back_to_search' in config):
    config['date_days_back_to_search'] = config['days_back_to_search']
    
  if ('movie_sort_1' not in config.keys() or config['movie_sort_1'] == ""):
    config['movie_sort_1'] = 'rating'
  if ('movie_sort_2' not in config.keys() or config['movie_sort_2'] == ""):
    config['movie_sort_2'] = 'title_sort'
    
  if ('movie_sort_1_reverse' not in config.keys() or config['movie_sort_1_reverse'] == ""):
    config['movie_sort_1_reverse'] = True
  if ('movie_sort_2_reverse' not in config.keys() or config['movie_sort_2_reverse'] == ""):
    config['movie_sort_2_reverse'] = False
  if ('movie_sort_3_reverse' not in config.keys() or config['movie_sort_3_reverse'] == ""):
    config['movie_sort_3_reverse'] = False
    
  if ('show_sort_1' not in config.keys() or config['show_sort_1'] == ""):
    config['show_sort_1'] = 'title_sort'
    
  if ('show_sort_1_reverse' not in config.keys() or config['show_sort_1_reverse'] == ""):
    config['show_sort_1_reverse'] = False
  if ('show_sort_2_reverse' not in config.keys() or config['show_sort_2_reverse'] == ""):
    config['show_sort_2_reverse'] = False
  if ('show_sort_3_reverse' not in config.keys() or config['show_sort_3_reverse'] == ""):
    config['show_sort_3_reverse'] = False
    
  if ('season_sort_1' not in config.keys() or config['season_sort_1'] == ""):
    config['season_sort_1'] = 'title_sort'
  if ('season_sort_2' not in config.keys() or config['season_sort_2'] == ""):
    config['season_sort_2'] = 'index'
    
  if ('season_sort_1_reverse' not in config.keys() or config['season_sort_1_reverse'] == ""):
    config['season_sort_1_reverse'] = False
  if ('season_sort_2_reverse' not in config.keys() or config['season_sort_2_reverse'] == ""):
    config['season_sort_2_reverse'] = False
  if ('season_sort_3_reverse' not in config.keys() or config['season_sort_3_reverse'] == ""):
    config['season_sort_3_reverse'] = False
    
  if ('episode_sort_1' not in config.keys() or config['episode_sort_1'] == ""):
    config['episode_sort_1'] = 'show_title_sort'
  if ('episode_sort_2' not in config.keys() or config['episode_sort_2'] == ""):
    config['episode_sort_2'] = 'season_index'
  if ('episode_sort_3' not in config.keys() or config['episode_sort_3'] == ""):
    config['episode_sort_3'] = 'index'
    
  if ('episode_sort_1_reverse' not in config.keys() or config['episode_sort_1_reverse'] == ""):
    config['episode_sort_1_reverse'] = False
  if ('episode_sort_2_reverse' not in config.keys() or config['episode_sort_2_reverse'] == ""):
    config['episode_sort_2_reverse'] = False
  if ('episode_sort_3_reverse' not in config.keys() or config['episode_sort_3_reverse'] == ""):
    config['episode_sort_3_reverse'] = False
    
  # The below code is replacing tokens
  if (config['web_domain'].rfind('/') < len(config['web_domain']) - len('/')):
    config['web_domain'] = config['web_domain'] + '/'
    
  if  (config['date_days_back_to_search'] == 31):
    now = datetime.datetime.now()
    if (now.month == 1):
      config['date_days_back_to_search'] = calendar.monthrange(now.year - 1, 12)[1]
    else:
      config['date_days_back_to_search'] = calendar.monthrange(now.year, now.month - 1)[1]
  
  for value in config:
    if (isinstance(config[value], str)):
      config[value] = config[value].replace('{past_day}', str((date.today() - timedelta(days=config['date_days_back_to_search'], hours=config['date_hours_back_to_search'], minutes=config['date_minutes_back_to_search'])).strftime(config['date_format'])))
      config[value] = config[value].replace('{current_day}', str(date.today().strftime(config['date_format'])))
      config[value] = config[value].replace('{website}', config['web_domain'] + config['web_path'])
      config[value] = config[value].replace('{path_sep}', os.path.sep)

  if (config['plex_data_folder'].rfind(os.path.sep) < len(config['plex_data_folder']) - len(os.path.sep)):
    config['plex_data_folder'] = config['plex_data_folder'] + os.path.sep
    
  if (config['plex_data_folder'].find('Plex Media Server') >= 0):
    config['plex_data_folder'] = config['plex_data_folder'][0:config['plex_data_folder'].find('Plex Media Server')]
    
  if (config['web_folder'].rfind(os.path.sep) < len(config['web_folder']) - len(os.path.sep)):
    config['web_folder'] = config['web_folder'] + os.path.sep
    
  if (config['web_domain'] != '' and config['web_domain'].rfind('/') < len(config['web_domain']) - len('/')):
    config['web_domain'] = config['web_domain'] + '/'
    
  if (config['logging_file_location'].rfind(os.path.sep) < len(config['logging_file_location']) - len(os.path.sep)):
    config['logging_file_location'] = config['logging_file_location'] + os.path.sep
  
    
def convertToHumanReadable(valuesToConvert):
  convertedValues = {}
  for value in valuesToConvert:
    convertedValues[value] = valuesToConvert[value]
    convertedValues[value + '_filter'] = [valuesToConvert[value]]
    if (not valuesToConvert[value]):
      continue
    if (value == 'duration'):
      if (valuesToConvert['real_duration']):
        convertedValues[value] = str(valuesToConvert['real_duration'] // 1000 // 60)
      else:
        convertedValues[value] = str(valuesToConvert[value] // 1000 // 60)
    elif (value == 'rating'):
      convertedValues[value] = str(int(valuesToConvert[value] * 10))
    elif (value == 'tags_genre' or value == 'tags_star' or value == 'tags_director'):
      convertedValues[value + '_filter'] = valuesToConvert[value].split('|')
      convertedValues[value] = valuesToConvert[value].replace('|', ', ')
  return convertedValues

def getSharedUserEmails():
  logging.info('getSharedUserEmails: begin')
  emails = []
  if (config['plex_username'] == '' or config['plex_password'] == ''):
    return emails
    
  url = 'https://my.plexapp.com/users/sign_in.json'
  logging.info('getSharedUserEmails: url = ' + url)
  base64string = 'Basic ' + base64.encodestring('%s:%s' % (config['plex_username'], config['plex_password'])).replace('\n', '')
  headers = {'Authorization': base64string, 'X-Plex-Client-Identifier': 'plexEmail'}
  logging.debug('getSharedUserEmails: headers = ' + str(headers))
  response = requests.post(url, headers=headers)
  logging.info('getSharedUserEmails: response = ' + str(response))
  logging.info('getSharedUserEmails: response = ' + str(response.text))
  token = json.loads(response.text)['user']['authentication_token'];
  logging.info('getSharedUserEmails: token = ' + token)
  
  url = 'https://plex.tv/pms/friends/all'
  logging.info('getSharedUserEmails: url = ' + url)
  headers = {'Accept': 'application/json', 'X-Plex-Token': token}
  logging.debug('getSharedUserEmails: headers = ' + str(headers))
  response = requests.get(url, headers=headers)
  logging.info('getSharedUserEmails: response = ' + str(response))
  logging.info('getSharedUserEmails: response = ' + str(response.text.encode('ascii', 'ignore')))
  
  parsed = XML(response.text.encode('ascii', 'ignore'))
  for elem in parsed:
    for name, value in sorted(elem.attrib.items()):
      if (name == 'email'):
        logging.info('getSharedUserEmails: adding email - ' + value.lower())
        emails.append(value.lower())
  
  logging.info('getSharedUserEmails: Returning shared emails')
  logging.debug('getSharedUserEmails: email list - ' + ' '.join(emails))
  return emails

def deleteImages():
  logging.info('deleteImages: begin')
  folder = config['web_folder'] + config['web_path'] + os.path.sep + 'images' + os.path.sep
  logging.info('deleteImages: deleting images from: ' + folder)
  for file in os.listdir(folder):
    if (file.endswith('.jpg')):
      logging.debug('deleteImages: deleting image: ' + folder + file)
      os.remove(folder + file)
  logging.info('deleteImages: end')
  
def processImage(imageHash, thumb, mediaType, seasonIndex, episodeIndex):
  logging.info('processImage: begin')
  logging.info('processImage: imageHash = ' + imageHash + ' - thumb = ' + thumb + ' - mediaType = ' + mediaType + ' - seasonIndex = ' + str(seasonIndex) + ' - episodeIndex = ' + str(episodeIndex))
  thumbObj = {}
  imgLocation = ''
  if (not thumb or thumb == ''):
    logging.info('processImage: thumb is either null or empty, returning no image')
    thumbObj['webImgPath'] = ''
    thumbObj['emailImgPath'] = ''
    return thumbObj
  
  if (thumb.find('http://') >= 0 or thumb.find('https://') >= 0):
    logging.info('processImage: thumb is already an externally hosted image')
    thumbObj['webImgPath'] = thumb
    thumbObj['emailImgPath'] = thumb
    return thumbObj
  else:
    if (thumb.find('media://') >= 0):
      logging.info('processImage: thumb begins with media://')
      thumb = thumb[8:len(thumb)]
      imgName = thumb[thumb.rindex('/') + 1:thumb.rindex('.')] + hash
      imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Media' + os.path.sep + 'localhost' + os.path.sep + '' + thumb
    elif (thumb.find('upload://') >= 0):
      logging.info('processImage: thumb begins with upload://')
      thumb = thumb[9:len(thumb)]
      category = thumb[0:thumb.index('/')]
      imgName = thumb[thumb.rindex('/') + 1:len(thumb)]
      if (mediaType == 'movie'):
        type = "Movies"
      else:
        type = "TV Shows"
      imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + type + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Uploads' + os.path.sep + category + os.path.sep + imgName
    else:
      thumb = thumb[11:len(thumb)]
      category = thumb[0:thumb.index('/')]
      imgName = thumb[thumb.index('_') + 1:len(thumb)]
      if (mediaType == 'movie'):
        indexer = thumb[thumb.index('/') + 1:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'Movies' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + '_stored' + os.path.sep + thumb
      elif (mediaType == 'show'):
        indexer = thumb[thumb.index('/') + 1:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'TV Shows' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + '_stored' + os.path.sep + thumb
      elif (mediaType == 'season'):
        indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'TV Shows' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + '_stored' + os.path.sep + thumb
      elif (mediaType == 'episode'):
        indexer = thumb[thumb.index('thumbs/') + 7:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'TV Shows' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + '_stored' + os.path.sep + thumb
      elif (mediaType == 'artist'):
        indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'Artists' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + '_stored' + os.path.sep + thumb
      elif (mediaType == 'album'):
        indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'Albums' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + '_stored' + os.path.sep + thumb
      imgName += '_' + imageHash
    webImgFullPath = config['web_domain'] + config['web_path'] + '/images/' + imgName + '.jpg'
    img = config['web_folder'] + config['web_path'] + os.path.sep + 'images' + os.path.sep + imgName + '.jpg'
    
    logging.info('processImage: imgLocation = ' + imgLocation)
    logging.info('processImage: webImgFullPath = ' + webImgFullPath)
    logging.info('processImage: img = ' + img)
    
    
    cloudinaryURL = ''
    if ('upload_use_cloudinary' in config and config['upload_use_cloudinary']):
      logging.info('processImage: Uploading to cloudinary')
      thumbObj['emailImgPath'] = webImgFullPath
      #imgurURL = uploadToImgur(imgLocation, imgName)
      cloudinaryURL = uploadToCloudinary(imgLocation)
    elif (config['web_enabled'] and config['email_use_web_images']):
      logging.info('processImage: Hosting image on local web server')
      thumbObj['emailImgPath'] = webImgFullPath
    elif (os.path.isfile(imgLocation)):
      logging.info('processImage: Attaching images to email')
      imgNames['Image_' + imgName] = imgLocation
      thumbObj['emailImgPath'] = 'cid:Image_' + imgName
    else:
      logging.info('processImage: No email image')
      thumbObj['emailImgPath'] = ''
      
    if (cloudinaryURL != ''):
      logging.info('processImage: Setting image paths to cloudinary')
      thumbObj['webImgPath'] = cloudinaryURL
      thumbObj['emailImgPath'] = cloudinaryURL
    elif (os.path.isfile(imgLocation) and config['web_enabled']):
      logging.info('processImage: Setting image paths to local and copying image to web folder')
      try:
        shutil.copy(imgLocation, img)
      except EnvironmentError, e:
        logging.warning('processImage: Failed to copy image - ' + repr(e))
        thumbObj['emailImgPath'] = ''
        thumbObj['webImgPath'] = ''
      else:
        thumbObj['webImgPath'] = 'images/' + imgName + '.jpg'
    else:
      thumbObj['webImgPath'] = ''
    
  return thumbObj
  
def uploadToImgur(imgToUpload, nameOfUpload):
  client_id = 'a0c7b089b62b220'
  headers = {"Authorization": "Client-ID " + client_id}
  url = "https://api.imgur.com/3/upload.json"
  if (os.path.isfile(imgToUpload)):
    response = requests.post(
      url, 
      headers = headers,
      data = {
        'image': b64encode(open(imgToUpload, 'rb').read()),
        'type': 'base64',
        'name': nameOfUpload + '.jpg',
        'title': nameOfUpload
      }
    )
    data = json.loads(response.text)['data'];
    return data['link']
  else:
    return ''
      
def uploadToCloudinary(imgToUpload):
  logging.info('uploadToCloudinary: begin')
  if (os.path.isfile(imgToUpload)):
    if (os.path.islink(imgToUpload)):
      imgToUpload = os.path.realpath(imgToUpload)
    if (imghdr.what(imgToUpload)):
      logging.info('uploadToCloudinary: start upload to cloudinary')
      response = cloudinary.uploader.upload(imgToUpload)
      logging.info('uploadToCloudinary: response = ' + str(response))
      url = response['secure_url'] if (config['upload_cloudinary_use_https']) else response['url']
      logging.info('uploadToCloudinary: url = ' + url)
      return url
    else:
      logging.info('uploadToCloudinary: not an image')
      return ''
  else:
    logging.info('uploadToCloudinary: file not located')
    return ''
    
def containsnonasciicharacters(str):
  return not all(ord(c) < 128 for c in str)   

def addheader(message, headername, headervalue):
  if containsnonasciicharacters(headervalue):
    h = Header(headervalue, 'utf-8')
    message[headername] = h
  else:
    message[headername] = headervalue    
  return message

def sendMail(email):
  #First check if email is in the unsubscribe list
  if email != '' and email[0].upper() in (name.upper() for name in config['email_unsubscribe']):
    print email[0] + ' is in the unsubscribe list.  Do not send an email.'
    return 0;
  gmail_user = config['email_username']
  gmail_pwd = config['email_password']
  smtp_address = config['email_smtp_address']
  smtp_port = config['email_smtp_port']
  use_ssl = config['email_use_ssl']
  FROM = formataddr((str(Header(config['email_from_name'])), config['email_from'])) if ('email_from_name' in config) else config['email_from']
  TO = email if (email != '') else config['email_to']
  SUBJECT = config['msg_email_subject']

  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg = addheader(msg, 'Subject', SUBJECT)
  msg['From'] = FROM

  # Create the body of the message (a plain-text and an HTML version).
  text = config['msg_email_teaser']
  
  # Record the MIME types of both parts - text/plain and text/html.
  if containsnonasciicharacters(emailHTML):
    htmltext = MIMEText(emailHTML, 'html','utf-8')
  else:
    htmltext = MIMEText(emailHTML, 'html')    

  if(containsnonasciicharacters(text)):
    plaintext = MIMEText(text,'plain','utf-8') 
  else:
    plaintext = MIMEText(text,'plain')
  
  #Create image headers
  for image in imgNames:
    fp = open(imgNames[image], 'rb')
    msgImage = MIMEImage(fp.read(), _subtype="jpg")
    fp.close()
    msgImage.add_header('Content-ID', '<' + image + '>')
    msg.attach(msgImage)

  # Attach parts into message container.
  # According to RFC 2046, the last part of a multipart message, in this case
  # the HTML message, is best and preferred.
  msg.attach(plaintext)
  msg.attach(htmltext)
  if (not config['email_use_bcc']):
    msg['To'] = ", ".join(TO)
  if (not use_ssl):
    server = smtplib.SMTP(smtp_address, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, msg.as_string())
    server.close()
  else:
    server = smtplib.SMTP_SSL(smtp_address, smtp_port)
    server.ehlo()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, msg.as_string())
    server.close()
    
  return 1;
  
def createEmailHTML():
  emailText = """<!DOCTYPE html>
        <html lang="en">

        <head>

            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="description" content="">
            <meta name="author" content="">

            <title>""" + config['msg_web_title'] + """</title>

            <!-- Bootstrap Core CSS -->
            <link href="css/bootstrap.min.css" rel="stylesheet">

            <!-- Custom CSS -->
            <link href="css/one-page-wonder.css" rel="stylesheet">
            
            <link rel="shortcut icon" href="images/favicon.ico">
            <link rel="apple-touch-icon" href="images/icon_iphone.png">
            <link rel="apple-touch-icon" sizes="72x72" href="images/icon_ipad.png">
            <link rel="apple-touch-icon" sizes="114x114" href="images/icon_iphone@2x.png">
            <link rel="apple-touch-icon" sizes="144x144" href="images/icon_ipad@2x.png">

            <style>
              .info {
              border: 1px solid;
              padding:15px 10px 15px 50px;
              background-repeat: no-repeat;
              background-position: 10px center;
              color: #00529B;
              background-color: #BDE5F8;
              background-image: url('../images/info.png');
              font-family:Arial, Helvetica, sans-serif; 
              font-size:20px;
              text-align: center;
            }
            </style>
            <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
            <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
            <!--[if lt IE 9]>
                <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
                <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
            <![endif]-->

        </head>

        <body>

            <p style="display:none;font-size:0;">""" + config['msg_email_teaser'] + """</p>
            <!-- Full Width Image Header -->
                    <table width="100%" style="background: #272727;">
                        <tr><td><h1 style="width: 100%; text-align: center; background: #272727 !important;"><font style="color: #F9AA03;">""" + config['msg_header1'] + """</font></h1></td></tr>
                        <tr><td><h2 style="width: 100%; text-align: center; background: #272727 !important;"><font style="color: #9A9A9A;">""" + config['msg_header2'] + """</font></h2></td></tr>
                        <tr><td><h2 style="width: 100%; text-align: center; background: #272727 !important;"><font style="color: #9A9A9A;">""" + config['msg_header3'] + """</font></h2></td></tr>
                    </table>

            <!-- Page Content -->
            <div class="container">"""
            
  emailText += emailNotice
  if (movieCount > 0 and config['filter_show_movies']):
    emailText += emailMovies + '<br/>&nbsp;'
  if (showCount > 0 and config['filter_show_shows']):
    emailText += emailTVShows + '<br/>&nbsp;'
  if (seasonCount > 0 and config['filter_show_seasons']):
    emailText += emailTVSeasons + '<br/>&nbsp;'
  if (episodeCount > 0 and config['filter_show_episodes']):
    emailText += emailTVEpisodes
  if (artistCount > 0 and config['filter_show_artists']):
    emailText += emailArtists + '<br/>&nbsp;'
  if (albumCount > 0 and config['filter_show_albums']):
    emailText += emailAlbums + '<br/>&nbsp;'
  if (songCount > 0 and config['filter_show_songs']):
    emailText += emailSongs
    
  if(not hasNewContent):
    emailText += """<div class="headline" style="background: #FFF !important; padding-top: 50px !important; padding-bottom: 50px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important;">""" + config['msg_no_new_content'] + """</h2>
        </div>"""
        
  emailText += """
            <!-- Footer -->
            <footer>
                <div class="row">
                    <div class="col-lg-12">
                        <p>Copyright &copy; Jake Waldron 2015</p>
                    </div>
                </div>
            </footer>

        </div>
        <!-- /.container -->

        <!-- jQuery -->
        <script src="js/jquery.js"></script>

        <!-- Bootstrap Core JavaScript -->
        <script src="js/bootstrap.min.js"></script>

    </body>

    </html>"""
    
  return emailText
  
def createWebHTML():
  htmlText = """<!DOCTYPE html>
      <html lang="en">

      <head>

          <meta charset="utf-8">
          <meta http-equiv="X-UA-Compatible" content="IE=edge">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta name="description" content="">
          <meta name="author" content="">

          <title>""" + config['msg_web_title'] + """</title>

          <!-- Bootstrap Core CSS -->
          <link href="css/bootstrap.min.css" rel="stylesheet">

          <!-- Custom CSS -->
          <link href="css/one-page-wonder.css" rel="stylesheet">
          
          <link rel="shortcut icon" href="images/favicon.ico">
          <link rel="apple-touch-icon" href="images/icon_iphone.png">
          <link rel="apple-touch-icon" sizes="72x72" href="images/icon_ipad.png">
          <link rel="apple-touch-icon" sizes="114x114" href="images/icon_iphone@2x.png">
          <link rel="apple-touch-icon" sizes="144x144" href="images/icon_ipad@2x.png">

          <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
          <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
          <!--[if lt IE 9]>
              <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
              <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
          <![endif]-->

      </head>

      <body>

          <!-- Navigation -->
          <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
              <div class="container">
                  <!-- Brand and toggle get grouped for better mobile display -->
                  <div class="navbar-header">
                      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
                          <span class="sr-only">Toggle navigation</span>
                          <span class="icon-bar"></span>
                          <span class="icon-bar"></span>
                          <span class="icon-bar"></span>
                      </button>
                      <a class="navbar-brand" href="#">""" + config['msg_top_link'] + """</a>
                  </div>
                  <!-- Collect the nav links, forms, and other content for toggling -->
                  <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                      <ul class="nav navbar-nav">"""
  if (movieCount > 0 and config['filter_show_movies']):
    htmlText += """
                          <li>
                              <a href="#movies-top">""" + config['msg_movies_link'] + """</a>
                          </li>"""
  if (showCount > 0 and config['filter_show_shows']):
    htmlText += """
                          <li>
                              <a href="#shows-top">""" + config['msg_shows_link'] + """</a>
                          </li>"""
  if (seasonCount > 0 and config['filter_show_seasons']):
    htmlText += """
                          <li>
                              <a href="#seasons-top">""" + config['msg_seasons_link'] + """</a>
                          </li>"""
  if (episodeCount > 0 and config['filter_show_episodes']):
    htmlText += """
                          <li>
                              <a href="#episodes-top">""" + config['msg_episodes_link'] + """</a>
                          </li>"""
  
  if (artistCount > 0 and config['filter_show_artists']):
    htmlText += """
                          <li>
                              <a href="#artists-top">""" + config['msg_artists_link'] + """</a>
                          </li>"""
  if (albumCount > 0 and config['filter_show_albums']):
    htmlText += """
                          <li>
                              <a href="#albums-top">""" + config['msg_albums_link'] + """</a>
                          </li>"""
  if (songCount > 0 and config['filter_show_songs']):
    htmlText += """
                          <li>
                              <a href="#songs-top">""" + config['msg_songs_link'] + """</a>
                          </li>"""
                          
  htmlText += """
                      </ul>
                  </div>
                  <!-- /.navbar-collapse -->
              </div>
              <!-- /.container -->
          </nav>

          <!-- Full Width Image Header -->
          <header class="header-image">
              <div class="headline">
                  <div class="container">
                      <h1>""" + config['msg_header1'] + """</h1>
                      <h2>""" + config['msg_header2'] + """</h2>
                  </div>
              </div>
          </header>

          <!-- Page Content -->
          <div class="container">"""
  
  htmlText += htmlNotice
  if (movieCount > 0 and config['filter_show_movies']):
    htmlText += htmlMovies + '<br/>&nbsp;'
  if (showCount > 0 and config['filter_show_shows']):
    htmlText += htmlTVShows + '<br/>&nbsp;'
  if (seasonCount > 0 and config['filter_show_seasons']):
    htmlText += htmlTVSeasons + '<br/>&nbsp;'
  if (episodeCount > 0 and config['filter_show_episodes']):
    htmlText += htmlTVEpisodes
  if (artistCount > 0 and config['filter_show_artists']):
    htmlText += htmlArtists + '<br/>&nbsp;'
  if (albumCount > 0 and config['filter_show_albums']):
    htmlText += htmlAlbums + '<br/>&nbsp;'
  if (songCount > 0 and config['filter_show_songs']):
    htmlText += htmlSongs
    
  if(not hasNewContent):
    htmlText += """<div class="headline" style="background: #FFF !important; padding-top: 50px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #000000;">""" + config['msg_no_new_content'] + """</font></h2>
        </div>"""
    
  htmlText += """<hr class="featurette-divider">
          <!-- Footer -->
          <footer>
              <div class="row">
                  <div class="col-lg-12">
                      <p>""" + config['msg_footer'] + """</p>
                  </div>
              </div>
          </footer>

      </div>
      <!-- /.container -->

      <!-- jQuery -->
      <script src="js/jquery.js"></script>

      <!-- Bootstrap Core JavaScript -->
      <script src="js/bootstrap.min.js"></script>

    </body>

    </html>"""
    
  return htmlText
  
def exceptionHandler(type, value, tb):
  logging.error("Logging an uncaught exception", exc_info=(type, value, tb))

#
#
#  Main Code
#
#

parser = argparse.ArgumentParser(description='This script aggregates all new TV and movie releases for the past x days then writes to your web directory and sends out an email.')
parser.add_argument('-c','--configfile', help='The path to a config file to be used in the running of this instance of the script.', default=os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep + 'config.conf', required=False)
parser.add_argument('-t','--test', help='Run this script in test mode - Sends email only to sender', action='store_true')
parser.add_argument('-n','--notice', help='Add a one-time message to the email/web page')
parser.add_argument('--version', help='Display the version of the script file', action='store_true')
args = vars(parser.parse_args())

if ('version' in args and args['version']):
  print 'Script Version: ' + SCRIPT_VERSION
  sys.exit()

if ('configfile' in args):
  configFile = args['configfile']

if (not os.path.isfile(configFile)):
  print configFile + ' does not exist'
  sys.exit()
  
config = {}
execfile(configFile, config)
replaceConfigTokens()

if (config['logging_enabled']):
  numeric_level = getattr(logging, config['logging_debug_level'], None)
  file_mode = 'a' if (config['logging_retain_previous_logs']) else 'w'
  if not isinstance(numeric_level, int):
    numeric_level = getattr(logging, 'INFO')
  if (config['logging_file_location'] != ''):
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s:%(message)s', filename=config['logging_file_location'] + 'plexEmail.log', filemode=file_mode)
  else:
    if not os.path.exists(os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep + 'logs'):
        os.makedirs(os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep + 'logs')
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s:%(message)s', filename=os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep + 'logs' + os.path.sep + 'plexEmail.log', filemode=file_mode)

  sys.excepthook = exceptionHandler

testMode = False

if ('test' in args):
  logging.info('Test flag found - setting script instance to test mode.')
  testMode = args['test']
else:
  logging.info('Test flag not found.')

if ('notice' in args and args['notice']):
  logging.info('Notice passed in: ' + args['notice'])
  config['msg_notice'] = args['notice']

if ('upload_use_cloudinary' in config and config['upload_use_cloudinary']):
  logging.info('Setting Cloudinary config values')
  cloudinary.config(
    cloud_name = config['upload_cloudinary_cloud_name'],
    api_key = config['upload_cloudinary_api_key'],
    api_secret = config['upload_cloudinary_api_secret'],
    upload_prefix = 'https://api.cloudinary.com' if ('upload_cloudinary_use_https' in config and config['upload_cloudinary_use_https']) else 'http://api.cloudinary.com'
  )
  logging.debug('Cloudinary config: ' + str(cloudinary.config))

plexWebLink = ''

if (config['filter_include_plex_web_link']):
  if (config['plex_web_server_guid'] == ''):
    plexWebLink = 'http://plex.tv/web/app#!/server/' + config['plex_web_server_guid'] + '/details/%2Flibrary%2Fmetadata%2F'
  else:
    logging.info('Including Plex Web Link - Getting machine identifier from the DLNA DB')
    DLNA_DB_FILE = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Plug-in Support' + os.path.sep + 'Databases' + os.path.sep + 'com.plexapp.dlna.db'
    logging.info('DLNA_DB_FILE = ' + DLNA_DB_FILE)
    
    if (os.path.isfile(DLNA_DB_FILE)):
      try:
        con = sqlite3.connect(DLNA_DB_FILE)
        cur = con.cursor()    
        cur.execute('SELECT machine_identifier FROM remote_servers WHERE url LIKE "http://127.0.0.1%";')
        for row in cur:
          plexWebLink = 'http://plex.tv/web/app#!/server/' + row[0] + '/details/%2Flibrary%2Fmetadata%2F'
          logging.info('plexWebLink = ' + plexWebLink)
      except sqlite3.OperationalError:
        logging.warning(DLNA_DB_FILE + ' is locked or does not have the correct permissions')
    else:
      logging.warning(DLNA_DB_FILE + ' does not exist')

DATABASE_FILE = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Plug-in Support' + os.path.sep + 'Databases' + os.path.sep + 'com.plexapp.plugins.library.db'
  
if (not os.path.isfile(DATABASE_FILE)):
  logging.error(DATABASE_FILE + ' does not exist. Please make sure the plex_data_folder value is correct.')
  print DATABASE_FILE + ' does not exist. Please make sure the plex_data_folder value is correct.'
  sys.exit()
  
con = sqlite3.connect(DATABASE_FILE)
con.text_factory = str

with con:
    libraryFilter = ''
    if (config['filter_libraries']):
      logging.info('Getting IDs of libraries to filter')
      cur = con.cursor()
      cur.execute('SELECT id, name FROM library_sections;')
      for row in cur:
        if (row[1].lower() in (library.lower() for library in config['filter_libraries'])):
          if (libraryFilter == ''):
            libraryFilter = ' AND ('
            libraryFilter += 'MD.library_section_id != ' + str(row[0])
          else:
            libraryFilter += ' AND MD.library_section_id != ' + str(row[0])
      if (libraryFilter != ''):
        libraryFilter += ') '
      logging.debug('libraryFilter = ' + libraryFilter)
      
    dateSearch = 'datetime(\'now\', \'localtime\', \'-' + str(config['date_days_back_to_search']) + ' days\', \'-' + str(config['date_hours_back_to_search']) + ' hours\', \'-' + str(config['date_minutes_back_to_search']) + ' minutes\')'
    logging.debug('dateSearch for DB query = ' + dateSearch)

    dbQuery = "SELECT MD.id, MD.parent_id, MD.metadata_type, MD.title, MD.title_sort, MD.original_title, MD.rating, MD.tagline, MD.summary, MD.content_rating, MD.duration, MD.user_thumb_url, MD.tags_genre, MD.tags_director, MD.tags_star, MD.year, MD.hash, MD.[index], MD.studio, ME.duration, MD.originally_available_at FROM metadata_items MD LEFT OUTER JOIN media_items ME ON MD.id = ME.metadata_item_id WHERE added_at >= " + dateSearch + " AND metadata_type >= 1 AND metadata_type <= 10 " + libraryFilter + " ORDER BY title_sort;"
    logging.info('Executing DB query: ' + dbQuery)
    cur = con.cursor()    
    cur.execute(dbQuery)

    response = {};
    logging.debug('Response:')
    for row in cur:
      response[row[0]] = {'id': row[0], 'parent_id': row[1], 'metadata_type': row[2], 'title': row[3], 'title_sort': row[4], 'original_title': row[5], 'rating': row[6], 'tagline': row[7], 'summary': row[8], 'content_rating': row[9], 'duration': row[10], 'user_thumb_url': row[11], 'tags_genre': row[12], 'tags_director': row[13], 'tags_star': row[14], 'year': row[15], 'hash': row[16], 'index': row[17], 'studio': row[18], 'real_duration': row[19], 'air_date': row[20]}
      logging.debug(response[row[0]])    
    
    emailNotice = ''
    htmlNotice = ''
    if (config['msg_notice']):
      logging.info('Generating html for the notice: ' + config['msg_notice'])
      emailNotice = """<br/>&nbsp;<div style="border: 1px solid; padding:15px 0px 15px 0px; background-repeat: no-repeat; background-position: 10px center; color: #00529B; background-color: #BDE5F8;font-family:Arial, Helvetica, sans-serif; font-size:20px; text-align: center;">""" + config['msg_notice'] + """</div><br/>&nbsp;"""
      htmlNotice = """<div class="container"><hr class="featurette-divider"><div class="info">""" + config['msg_notice'] + """</div>"""
    emailMovies = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_movies_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlMovies = """<hr class="featurette-divider" id="movies-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_movies_header'] + """</h2>
        </div>"""
    emailTVShows = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_shows_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="shows-top"><br/>&nbsp;"""
    htmlTVShows = """<hr class="featurette-divider" id="shows-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_shows_header'] + """</h2>
        </div>"""
    emailTVSeasons = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_seasons_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="seasons-top"><br/>&nbsp;"""
    htmlTVSeasons = """<hr class="featurette-divider" id="seasons-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_seasons_header'] + """</h2>
        </div>"""
    emailTVEpisodes = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_episodes_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="episodes-top"><br/>&nbsp;"""
    htmlTVEpisodes = """<hr class="featurette-divider" id="episodes-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_episodes_header'] + """</h2>
        </div>"""
    emailArtists = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_artists_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="artists-top"><br/>&nbsp;"""
    htmlArtists = """<hr class="featurette-divider" id="artists-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_artists_header'] + """</h2>
        </div>"""
    emailAlbums = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_albums_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="albums-top"><br/>&nbsp;"""
    htmlAlbums= """<hr class="featurette-divider" id="albums-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_albums_header'] + """</h2>
        </div>"""
    emailSongs = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_songs_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="songs-top"><br/>&nbsp;"""
    htmlSongs = """<hr class="featurette-divider" id="songs-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_songs_header'] + """</h2>
        </div>"""
    movies = {}
    tvShows = {}
    tvSeasons = {}
    tvEpisodes = {}
    artists = {}
    albums = {}
    songs = {}
    imgNames = {}
    movieCount = 0
    showCount = 0
    seasonCount = 0
    episodeCount = 0
    artistCount = 0
    albumCount = 0
    songCount = 0
    if (config['web_enabled'] and 'web_delete_previous_images' in config and config['web_delete_previous_images']):
      deleteImages()
    for item in response:
      #Handle New Movies
      if (response[item]['metadata_type'] == 1):
        movies[response[item]['id']] = response[item]
      
      #TV
      if (response[item]['metadata_type'] == 2):
        tvShows[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 3):
        tvSeasons[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 4):
        tvEpisodes[response[item]['id']] = response[item]
      
      #Music      
      if (response[item]['metadata_type'] == 8):
        artists[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 9):
        albums[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 10):
        songs[response[item]['id']] = response[item]
        
    if ('movie_sort_3' in config and config['movie_sort_3'] != ''):
      movies = OrderedDict(sorted(movies.iteritems(), key=lambda t: t[1][config['movie_sort_3']], reverse=config['movie_sort_3_reverse']))
    if ('movie_sort_2' in config and config['movie_sort_2'] != ''):
      movies = OrderedDict(sorted(movies.iteritems(), key=lambda t: t[1][config['movie_sort_2']], reverse=config['movie_sort_2_reverse']))
    if ('movie_sort_1' in config and config['movie_sort_1'] != ''):
      movies = OrderedDict(sorted(movies.iteritems(), key=lambda t: t[1][config['movie_sort_1']], reverse=config['movie_sort_1_reverse']))
    
    for movie in movies:
      movies[movie] = convertToHumanReadable(movies[movie])
      title = ''
      if ('original_title' in movies[movie] and movies[movie]['original_title'] != ''):
        title += movies[movie]['original_title'] + ' AKA '
      title += movies[movie]['title']
      hash = str(movies[movie]['hash'])
      imageInfo = {}
      imageInfo['thumb'] = movies[movie]['user_thumb_url']
      imageInfo = processImage(hash, imageInfo['thumb'], 'movie', 0, 0)
      
      skipItem = False
      emailText = ''
      htmlText = ''
      if (config['filter_include_plex_web_link']):
        pwLink = plexWebLink + str(movies[movie]['id'])
      else:
        pwLink = ''
      
      emailText += '<table><tr width="100%">'
      if (config['filter_show_email_images']):
        emailText += '<td width="200">'
        emailText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a>'
        emailText += '</td>'
      emailText += '<td><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      htmlText += '<div class="featurette" id="movies">'
      htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      
      sections = config['filter_sections_movies']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (movies[movie][section[0]] in sections[section[0]]['exclude'] or len(set(movies[movie][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and movies[movie][section[0]] not in sections[section[0]]['include'] and len(set(movies[movie][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
          skipItem = True
        if (sections[section[0]]['show'] and movies[movie][section[0]] and movies[movie][section[0]] != ''):
          displayText = str(movies[movie][section[0]])
          if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
            displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
          emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
          htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
      titleFilter = []
        
      if (movies[movie]['title'] in config['filter_movies_exclude'] or len(set(titleFilter).intersection(config['filter_movies_exclude'])) > 0 or (config['filter_movies_include'] and movies[movie]['title'] not in config['filter_movies_include'] and len(set(titleFilter).intersection(config['filter_movies_include'])) == 0)):
        skipItem = True
        
      if (not skipItem):
        movieCount += 1
        emailMovies += emailText
        htmlMovies += htmlText
    
    if ('show_sort_3' in config and config['show_sort_3'] != ''):
      tvShows = OrderedDict(sorted(tvShows.iteritems(), key=lambda t: t[1][config['show_sort_3']], reverse=config['show_sort_3_reverse']))
    if ('show_sort_2' in config and config['show_sort_2'] != ''):
      tvShows = OrderedDict(sorted(tvShows.iteritems(), key=lambda t: t[1][config['show_sort_2']], reverse=config['show_sort_2_reverse']))
    if ('show_sort_1' in config and config['show_sort_1'] != ''):
      tvShows = OrderedDict(sorted(tvShows.iteritems(), key=lambda t: t[1][config['show_sort_1']], reverse=config['show_sort_1_reverse']))
    
    for show in tvShows:
      tvShows[show] = convertToHumanReadable(tvShows[show])
      title = ''
      if (tvShows[show]['original_title'] != ''):
        title += tvShows[show]['original_title'] + ' AKA '
      title += tvShows[show]['title']
      hash = str(tvShows[show]['hash'])
      imageInfo = {}
      imageInfo['thumb'] = tvShows[show]['user_thumb_url']
      imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
      
      skipItem = False
      emailText = ''
      htmlText = ''
      if (config['filter_include_plex_web_link']):
        pwLink = plexWebLink + str(tvShows[show]['id'])
      else:
        pwLink = ''
      
      emailText += '<table><tr width="100%">'
      if (config['filter_show_email_images']):
        emailText += '<td width="200"><a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a></td>'
      emailText += '<td><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      htmlText += '<div class="featurette" id="shows">'
      htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      
      sections = config['filter_sections_TV']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (tvShows[show][section[0]] in sections[section[0]]['exclude'] or len(set(tvShows[show][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and tvShows[show][section[0]] not in sections[section[0]]['include'] and len(set(tvShows[show][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
          skipItem = True
        if (sections[section[0]]['show'] and tvShows[show][section[0]] and tvShows[show][section[0]] != ''):
          displayText = str(tvShows[show][section[0]])
          if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
            displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
          emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
          htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
      titleFilter = []
        
      if (tvShows[show]['title'] in config['filter_shows_exclude'] or len(set(titleFilter).intersection(config['filter_shows_exclude'])) > 0 or (config['filter_shows_include'] and tvShows[show]['title'] not in config['filter_shows_include'] and len(set(titleFilter).intersection(config['filter_shows_include'])) == 0)):
        skipItem = True
        
      if (not skipItem):
        showCount += 1
        emailTVShows += emailText
        htmlTVShows += htmlText
    
    for season in tvSeasons:
      cur2 = con.cursor()
      cur2.execute("SELECT title, title_sort, original_title, rating, tagline, summary, content_rating, duration, tags_genre, tags_director, tags_star, year, hash, user_thumb_url, studio FROM metadata_items WHERE id = " + str(tvSeasons[season]['parent_id']) + ";")

      for row in cur2:
        tvSeasons[season]['title'] = row[0]
        tvSeasons[season]['title_sort'] = row[1]
        tvSeasons[season]['original_title'] = row[2]
        tvSeasons[season]['rating'] = row[3]
        tvSeasons[season]['tagline'] = row[4]
        tvSeasons[season]['summary'] = row[5]
        tvSeasons[season]['content_rating'] = row[6]
        tvSeasons[season]['duration'] = row[7]
        tvSeasons[season]['tags_genre'] = row[8]
        tvSeasons[season]['tags_director'] = row[9]
        tvSeasons[season]['tags_star'] = row[10]
        tvSeasons[season]['year'] = row[11]
        tvSeasons[season]['parent_hash'] = row[12]
        tvSeasons[season]['parent_thumb_url'] = row[13]
        tvSeasons[season]['studio'] = row[14]
          
    if ('season_sort_3' in config and config['season_sort_3'] != ''):
      tvSeasons = OrderedDict(sorted(tvSeasons.iteritems(), key=lambda t: t[1][config['season_sort_3']], reverse=config['season_sort_3_reverse']))
    if ('season_sort_2' in config and config['season_sort_2'] != ''):
      tvSeasons = OrderedDict(sorted(tvSeasons.iteritems(), key=lambda t: t[1][config['season_sort_2']], reverse=config['season_sort_2_reverse']))
    if ('season_sort_1' in config and config['season_sort_1'] != ''):
      tvSeasons = OrderedDict(sorted(tvSeasons.iteritems(), key=lambda t: t[1][config['season_sort_1']], reverse=config['season_sort_1_reverse']))
    
    for season in tvSeasons:
      tvSeasons[season] = convertToHumanReadable(tvSeasons[season])
      title = ''
      if (tvSeasons[season]['original_title'] != ''):
        title += tvSeasons[season]['original_title'] + ' AKA '
      title += tvSeasons[season]['title']
      imageInfo = {}
      if (tvSeasons[season]['user_thumb_url'] != ''):
        imageInfo['thumb'] = tvSeasons[season]['user_thumb_url']
        hash = str(tvSeasons[season]['parent_hash'])
        imageInfo = processImage(hash, imageInfo['thumb'], 'season', tvSeasons[season]['index'], 0)
      else:
        imageInfo['thumb'] = tvSeasons[season]['parent_thumb_url']
        hash = str(tvSeasons[season]['parent_hash'])
        imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
      
      skipItem = False
      emailText = ''
      htmlText = ''
      if (config['filter_include_plex_web_link']):
        pwLink = plexWebLink + str(tvSeasons[season]['id'])
      else:
        pwLink = ''
      
      emailText += '<table><tr width="100%">'
      if (config['filter_show_email_images']):
        emailText += '<td width="200"><a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a></td>'
      emailText += '<td><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      emailText += '<p class="lead"><b>Season ' + str(tvSeasons[season]['index']) + '</b></p>'
      htmlText += '<div class="featurette" id="shows">'
      htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      htmlText += '<p class="lead"><b>Season ' + str(tvSeasons[season]['index']) + '</b></p>'      
      
      sections = config['filter_sections_TV']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (tvSeasons[season][section[0]] in sections[section[0]]['exclude'] or len(set(tvSeasons[season][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and tvSeasons[season][section[0]] not in sections[section[0]]['include'] and len(set(tvSeasons[season][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
          skipItem = True
        if (sections[section[0]]['show'] and tvSeasons[season][section[0]] and tvSeasons[season][section[0]] != ''):
          displayText = str(tvSeasons[season][section[0]])
          if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
            displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
          emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
          htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
      titleFilter = []
        
      if (tvSeasons[season]['title'] in config['filter_seasons_exclude'] or len(set(titleFilter).intersection(config['filter_seasons_exclude'])) > 0 or (config['filter_seasons_include'] and tvSeasons[season]['title'] not in config['filter_seasons_include'] and len(set(titleFilter).intersection(config['filter_seasons_include'])) == 0)):
        skipItem = True
          
      if (not skipItem):
        seasonCount += 1
        emailTVSeasons += emailText
        htmlTVSeasons += htmlText
  
    modifiedTVEpisodes = dict(tvEpisodes)
    for episode in tvEpisodes:
      logging.debug('main: hash = ' + tvEpisodes[episode]['hash'])
      logging.debug('main: user_thumb_url = ' + tvEpisodes[episode]['user_thumb_url'])
      cur2 = con.cursor()
      if (tvEpisodes[episode]['parent_id']):
        logging.info('main: tvEpisodes[episode][\'parent_id\'] = ' + str(tvEpisodes[episode]['parent_id']))
        cur2.execute("SELECT user_thumb_url, parent_id, [index], hash FROM metadata_items WHERE id = ?;", (str(tvEpisodes[episode]['parent_id']),))

        for row in cur2:
          tvEpisodes[episode]['season_thumb_url'] = row[0]
          parent_id = row[1]
          tvEpisodes[episode]['season_index'] = row[2]
          tvEpisodes[episode]['season_hash'] = row[3]
          logging.debug('main: season_hash = ' + row[3])
          logging.debug('main: season_thumb_url = ' + row[0])
          
          cur3 = con.cursor()
          cur3.execute("SELECT title, title_sort, original_title, content_rating, duration, tags_genre, tags_star, hash, user_thumb_url, studio FROM metadata_items WHERE id = " + str(parent_id) + ";")
          
          for row2 in cur3:
            tvEpisodes[episode]['show_title'] = row2[0]
            tvEpisodes[episode]['show_title_sort'] = row2[1]
            tvEpisodes[episode]['show_original_title'] = row2[2]
            tvEpisodes[episode]['content_rating'] = row2[3]
            tvEpisodes[episode]['duration'] = row2[4]
            tvEpisodes[episode]['tags_genre'] = row2[5]
            tvEpisodes[episode]['tags_star'] = row2[6]
            tvEpisodes[episode]['show_hash'] = row2[7]
            logging.debug('main: show_hash = ' + row2[7])
            tvEpisodes[episode]['show_thumb_url'] = row2[8]
            logging.debug('main: show_thumb_url = ' + row2[8])
            tvEpisodes[episode]['studio'] = row2[9]
      else:
        logging.info('main: tvEpisodes[episode][\'parent_id\'] = None')
        del modifiedTVEpisodes[episode]
        
    tvEpisodes = dict(modifiedTVEpisodes)
          
    if ('episode_sort_3' in config and config['episode_sort_3'] != ''):
      tvEpisodes = OrderedDict(sorted(tvEpisodes.iteritems(), key=lambda t: t[1][config['episode_sort_3']], reverse=config['episode_sort_3_reverse']))
    if ('episode_sort_2' in config and config['episode_sort_2'] != ''):
      tvEpisodes = OrderedDict(sorted(tvEpisodes.iteritems(), key=lambda t: t[1][config['episode_sort_2']], reverse=config['episode_sort_2_reverse']))
    if ('episode_sort_1' in config and config['episode_sort_1'] != ''):
      tvEpisodes = OrderedDict(sorted(tvEpisodes.iteritems(), key=lambda t: t[1][config['episode_sort_1']], reverse=config['episode_sort_1_reverse']))
    
    for episode in tvEpisodes:
      if (tvEpisodes[episode]['parent_id'] not in tvSeasons):
        tvEpisodes[episode] = convertToHumanReadable(tvEpisodes[episode])
        showTitle = ''
        if (tvEpisodes[episode]['show_original_title'] != ''):
          showTitle += tvEpisodes[episode]['show_original_title'] + ' AKA '
        showTitle += tvEpisodes[episode]['show_title']
        title = ''
        if (tvEpisodes[episode]['original_title'] != ''):
          title += tvEpisodes[episode]['original_title'] + ' AKA '
        title += tvEpisodes[episode]['title']
        imageInfo = {}
        imageTypeToUse = 'show' if (tvEpisodes[episode]['show_thumb_url'] != '' and config['filter_episode_thumbnail_type'] == 'show') else 'season' if (tvEpisodes[episode]['season_thumb_url'] != '' and config['filter_episode_thumbnail_type'] == 'season') else 'episode' if (tvEpisodes[episode]['user_thumb_url'] != '') else ''
        logging.info('main: imageTypeToUse = ' + imageTypeToUse)
        if (imageTypeToUse == 'episode'):
          imageInfo['thumb'] = tvEpisodes[episode]['user_thumb_url']
          hash = str(tvEpisodes[episode]['show_hash'])
          imageInfo = processImage(hash, imageInfo['thumb'], 'episode', tvEpisodes[episode]['season_index'], tvEpisodes[episode]['index'])
        elif (imageTypeToUse == 'season'):
          imageInfo['thumb'] = tvEpisodes[episode]['season_thumb_url']
          hash = str(tvEpisodes[episode]['show_hash'])
          imageInfo = processImage(hash, imageInfo['thumb'], 'season', tvEpisodes[episode]['season_index'], 0)
        elif (imageTypeToUse == 'show'):
          imageInfo['thumb'] = tvEpisodes[episode]['show_thumb_url']
          hash = str(tvEpisodes[episode]['show_hash'])
          imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
        
        skipItem = False
        emailText = ''
        htmlText = ''
        if (config['filter_include_plex_web_link']):
          pwLink = plexWebLink + str(tvEpisodes[episode]['id'])
        else:
          pwLink = ''
      
        emailText += '<table><tr width="100%">'
        if (config['filter_show_email_images'] and len(imageInfo) != 0):
          emailText += '<td width="200"><a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a></td>'
        emailText += '<td><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + showTitle.decode('utf-8') + '</a></h2>'
        emailText += '<p class="lead"><i>S' + str(tvEpisodes[episode]['season_index']) + ' E' + str(tvEpisodes[episode]['index']) + ': ' + title.decode('utf-8') + '</i></p>'
        htmlText += '<div class="featurette" id="shows">'
        if (len(imageInfo) != 0):
          htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
        htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + showTitle.decode('utf-8') + '</a></h2>'
        htmlText += '<p class="lead"><i>S' + str(tvEpisodes[episode]['season_index']) + ' E' + str(tvEpisodes[episode]['index']) + ': ' + title.decode('utf-8') + '</i></p>'
        
        sections = config['filter_sections_TV']
        for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
          if (tvEpisodes[episode][section[0]] in sections[section[0]]['exclude'] or len(set(tvEpisodes[episode][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and tvEpisodes[episode][section[0]] not in sections[section[0]]['include'] and len(set(tvEpisodes[episode][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
            skipItem = True
          if (sections[section[0]]['show'] and tvEpisodes[episode][section[0]] and tvEpisodes[episode][section[0]] != ''):
            displayText = str(tvEpisodes[episode][section[0]])
            if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
              displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
            emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
            htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
        
        emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
        htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
        
        titleFilter = []
        
        if (tvEpisodes[episode]['show_title'] in config['filter_episodes_exclude'] or len(set(titleFilter).intersection(config['filter_episodes_exclude'])) > 0 or (config['filter_episodes_include'] and tvEpisodes[episode]['show_title'] not in config['filter_episodes_include'] and len(set(titleFilter).intersection(config['filter_episodes_include'])) == 0)):
          skipItem = True
        
        if (not skipItem):
          episodeCount += 1
          emailTVEpisodes += emailText
          htmlTVEpisodes += htmlText

    if ('artist_sort_3' in config and config['artist_sort_3'] != ''):
      artists = OrderedDict(sorted(artists.iteritems(), key=lambda t: t[1][config['artist_sort_3']], reverse=config['artist_sort_3_reverse']))
    if ('artist_sort_2' in config and config['artist_sort_2'] != ''):
      artists = OrderedDict(sorted(artists.iteritems(), key=lambda t: t[1][config['artist_sort_2']], reverse=config['artist_sort_2_reverse']))
    if ('artist_sort_1' in config and config['artist_sort_1'] != ''):
      artists = OrderedDict(sorted(artists.iteritems(), key=lambda t: t[1][config['artist_sort_1']], reverse=config['artist_sort_1_reverse']))
    
    for artist in artists:
      artists[artist] = convertToHumanReadable(artists[artist])
      title = ''
      if (artists[artist]['original_title'] != ''):
        title += artists[artist]['original_title'] + ' AKA '
      title += artists[artist]['title']
      hash = str(artists[artist]['hash'])
      imageInfo = {}
      imageInfo['thumb'] = artists[artist]['user_thumb_url']
      imageInfo = processImage(hash, imageInfo['thumb'], 'artist', 0, 0)
      
      skipItem = False
      emailText = ''
      htmlText = ''
      if (config['filter_include_plex_web_link']):
        pwLink = plexWebLink + str(artists[artist]['id'])
      else:
        pwLink = ''
      
      emailText += '<table><tr width="100%">'
      if (config['filter_show_email_images']):
        emailText += '<td width="200"><a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a></td>'
      emailText += '<td><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      htmlText += '<div class="featurette" id="artists">'
      htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      
      sections = config['filter_sections_Music']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (section[0] != 'track_list'):
          if (artists[artist][section[0]] in sections[section[0]]['exclude'] or len(set(artists[artist][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and artists[artist][section[0]] not in sections[section[0]]['include'] and len(set(artists[artist][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
            skipItem = True
          if (sections[section[0]]['show'] and artists[artist][section[0]] and artists[artist][section[0]] != ''):
            displayText = str(artists[artist][section[0]])
            if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
              displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
            emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
            htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
      titleFilter = []
        
      if (artists[artist]['title'] in config['filter_artists_exclude'] or len(set(titleFilter).intersection(config['filter_artists_exclude'])) > 0 or (config['filter_artists_include'] and artists[artist]['title'] not in config['filter_artists_include'] and len(set(titleFilter).intersection(config['filter_artists_include'])) == 0)):
        skipItem = True
        
      if (not skipItem):
        artistCount += 1
        emailArtists += emailText
        htmlArtists += htmlText
  
    for album in albums:
      cur2 = con.cursor()
      cur2.execute("SELECT title, title_sort, original_title, rating, tagline, summary, content_rating, duration, tags_genre, tags_director, tags_star, year, hash, user_thumb_url, studio FROM metadata_items WHERE id = " + str(albums[album]['parent_id']) + ";")

      for row in cur2:
        albums[album]['title'] = row[0] + ' - ' + albums[album]['title']
        albums[album]['title_sort'] = row[1] + ' - ' + albums[album]['title_sort']
        albums[album]['original_title'] = row[2]
        albums[album]['rating'] = row[3]
        albums[album]['tagline'] = row[4]
        albums[album]['summary'] = row[5]
        albums[album]['content_rating'] = row[6]
        albums[album]['duration'] = row[7]
        albums[album]['tags_genre'] = row[8]
        albums[album]['tags_director'] = row[9]
        albums[album]['tags_star'] = row[10]
        albums[album]['year'] = row[11]
        albums[album]['parent_hash'] = row[12]
        albums[album]['parent_thumb_url'] = row[13]
        albums[album]['studio'] = row[14]
        
      cur2 = con.cursor()
      cur2.execute("SELECT MD.id, MD.title, MD.title_sort, MD.original_title, MD.[index], ME.duration, ME.audio_codec FROM metadata_items MD LEFT OUTER JOIN media_items ME ON MD.id = ME.metadata_item_id WHERE parent_id = " + str(albums[album]['id']) + ";")
      
      albums[album]['tracks'] = {}
      for row in cur2:
        duration = row[5]
        try:
          duration /= 1000
          seconds = duration % 60
          duration /= 60
          minutes = duration % 60
          duration /= 60
          hours = duration
          duration = str(hours) + ':' if (hours > 0) else ''
          duration += str(minutes).zfill(2) + ':' + str(seconds).zfill(2)
        except TypeError:
          duration = 'N/A'
        albums[album]['tracks'][row[4]] = {'id': row[0], 'title': row[1], 'title_sort': row[2], 'original_title': row[3], 'index': row[4], 'duration': duration, 'codec': row[6]}
          
    if ('album_sort_3' in config and config['album_sort_3'] != ''):
      albums = OrderedDict(sorted(albums.iteritems(), key=lambda t: t[1][config['album_sort_3']], reverse=config['album_sort_3_reverse']))
    if ('album_sort_2' in config and config['album_sort_2'] != ''):
      albums = OrderedDict(sorted(albums.iteritems(), key=lambda t: t[1][config['album_sort_2']], reverse=config['album_sort_2_reverse']))
    if ('album_sort_1' in config and config['album_sort_1'] != ''):
      albums = OrderedDict(sorted(albums.iteritems(), key=lambda t: t[1][config['album_sort_1']], reverse=config['album_sort_1_reverse']))
    
    for album in albums:
      albums[album] = convertToHumanReadable(albums[album])
      title = ''
      if (albums[album]['original_title'] != ''):
        title += albums[album]['original_title'] + ' AKA '
      title += albums[album]['title']
      imageInfo = {}
      if (albums[album]['user_thumb_url'] != ''):
        imageInfo['thumb'] = albums[album]['user_thumb_url']
        imageInfo = processImage(str(albums[album]['hash']), imageInfo['thumb'], 'album', albums[album]['index'], 0)
      else:
        imageInfo['thumb'] = albums[album]['parent_thumb_url']
        imageInfo = processImage(str(albums[album]['parent_hash']), imageInfo['thumb'], 'artist', 0, 0)

      skipItem = False
      emailText = ''
      htmlText = ''
      if (config['filter_include_plex_web_link']):
        pwLink = plexWebLink + str(albums[album]['id'])
      else:
        pwLink = ''
      
      emailText += '<table><tr width="100%" style="width: 100% !important">'
      if (config['filter_show_email_images']):
        emailText += '<td width="200" style="width: 200px !important"><a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a></td>'
      emailText += '<td width="1080" style="width: 1080px !important"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      htmlText += '<div class="featurette" id="albums">'
      htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + title.decode('utf-8') + '</a></h2>'
      
      tracklistEmailText = ''
      tracklistHTMLText = ''
      sections = config['filter_sections_Music']
      trackCount = 0
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (section[0] == 'track_list'):
          if (sections[section[0]]['show']):
            tracklistEmailText += '<br/><table width="100%" style="width: 100% !important"><tr><th align="left" style="text-align: left;">' + sections[section[0]]['headerText']['trackNumber'] + '</th><th align="left" style="text-align: left;">' + sections[section[0]]['headerText']['songName'] + '</th><th align="left" style="text-align: left;">' + sections[section[0]]['headerText']['artistName'] + '</th><th align="right" style="text-align: right;">' + sections[section[0]]['headerText']['duration'] + '</th></tr><tr><td colspan="5"><hr></td></tr>'
            tracklistHTMLText += '<br/><table width="100%" style="width: 100% !important"><tr><th align="left" style="text-align: left;">' + sections[section[0]]['headerText']['trackNumber'] + '</th><th align="left" style="text-align: left;">' + sections[section[0]]['headerText']['songName'] + '</th><th align="left" style="text-align: left;">' + sections[section[0]]['headerText']['artistName'] + '</th><th align="right" style="text-align: right;">' + sections[section[0]]['headerText']['duration'] + '</th></tr><tr><td colspan="5"><hr></td></tr>'
            for track in albums[album]['tracks']:
              tracklistEmailText += '<tr width="100%" style="width: 100% !important"><td width="5%" style="width: 5% !important" class="track_index">' + str(albums[album]['tracks'][track]['index']).decode('utf-8') + '</td><td width="35%" style="width: 50% !important" class="track_title">' + albums[album]['tracks'][track]['title'].decode('utf-8') + '</td><td width="30%" style="width: 35% !important" class="track_original_title">' + albums[album]['tracks'][track]['original_title'].decode('utf-8') + '</td><td width="15%" align="right" style="width: 15% !important; text-align: right;" class="track_duration">' + str(albums[album]['tracks'][track]['duration']).decode('utf-8') + '</td></tr>'
              tracklistHTMLText += '<tr width="100%" style="width: 100% !important"><td width="5%" style="width: 5% !important" class="track_index">' + str(albums[album]['tracks'][track]['index']).decode('utf-8') + '</td><td width="35%" style="width: 50% !important" class="track_title">' + albums[album]['tracks'][track]['title'].decode('utf-8') + '</td><td width="35%" style="width: 30% !important" class="track_original_title">' + albums[album]['tracks'][track]['original_title'].decode('utf-8') + '</td><td width="15%" align="right" style="width: 15% !important; text-align: right;" class="track_duration">' + str(albums[album]['tracks'][track]['duration']).decode('utf-8') + '</td></tr>'
              trackCount += 1
            tracklistEmailText += '</table>'
            tracklistHTMLText += '</table>'
        else:
          if (albums[album][section[0]] in sections[section[0]]['exclude'] or len(set(albums[album][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and albums[album][section[0]] not in sections[section[0]]['include'] and len(set(albums[album][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
            skipItem = True
          if (sections[section[0]]['show'] and albums[album][section[0]] and albums[album][section[0]] != ''):
            displayText = str(albums[album][section[0]])
            if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
              displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
            emailText += '<p style="width: 100% !important" class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
            htmlText += '<p style="width: 100% !important" class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table>'
      emailText += tracklistEmailText if (trackCount > 0) else ''
      emailText += '<br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div>'
      htmlText += tracklistHTMLText if (trackCount > 0) else ''
      htmlText += '<br/>&nbsp;<br/>&nbsp;'
      
      titleFilter = []
        
      if (albums[album]['title'] in config['filter_albums_exclude'] or len(set(titleFilter).intersection(config['filter_albums_exclude'])) > 0 or (config['filter_albums_include'] and albums[album]['title'] not in config['filter_albums_include'] and len(set(titleFilter).intersection(config['filter_albums_include'])) == 0)):
        skipItem = True
          
      if (not skipItem):
        albumCount += 1
        emailAlbums += emailText
        htmlAlbums += htmlText

    # for song in songs:
      # cur2 = con.cursor()
      # cur2.execute("SELECT user_thumb_url, parent_id, [index] FROM metadata_items WHERE id = " + str(songs[song]['parent_id']) + ";")

      # for row in cur2:
        # songs[song]['season_thumb_url'] = row[0]
        # parent_id = row[1]
        # songs[song]['season_index'] = row[2]
        
        # cur3 = con.cursor()
        # cur3.execute("SELECT title, title_sort, original_title, content_rating, duration, tags_genre, tags_star, hash, user_thumb_url, studio FROM metadata_items WHERE id = " + str(parent_id) + ";")
        
        # for row2 in cur3:
          # songs[song]['show_title'] = row2[0]
          # songs[song]['show_title_sort'] = row2[1]
          # songs[song]['show_original_title'] = row2[2]
          # songs[song]['content_rating'] = row2[3]
          # songs[song]['duration'] = row2[4]
          # songs[song]['tags_genre'] = row2[5]
          # songs[song]['tags_star'] = row2[6]
          # songs[song]['hash'] = row2[7]
          # songs[song]['show_thumb_url'] = row2[8]
          # songs[song]['studio'] = row2[9]
          
    # if ('song_sort_3' in config and config['song_sort_3'] != ''):
      # songs = OrderedDict(sorted(songs.iteritems(), key=lambda t: t[1][config['song_sort_3']], reverse=config['song_sort_3_reverse']))
    # if ('song_sort_2' in config and config['song_sort_2'] != ''):
      # songs = OrderedDict(sorted(songs.iteritems(), key=lambda t: t[1][config['song_sort_2']], reverse=config['song_sort_2_reverse']))
    # if ('song_sort_1' in config and config['song_sort_1'] != ''):
      # songs = OrderedDict(sorted(songs.iteritems(), key=lambda t: t[1][config['song_sort_1']], reverse=config['song_sort_1_reverse']))
    
    # for song in songs:
      # if (songs[song]['parent_id'] not in tvSeasons):
        # songs[song] = convertToHumanReadable(songs[song])
        # showTitle = ''
        # if (songs[song]['show_original_title'] != ''):
          # showTitle += songs[song]['show_original_title'] + ' AKA '
        # showTitle += songs[song]['show_title']
        # title = ''
        # if (songs[song]['original_title'] != ''):
          # title += songs[song]['original_title'] + ' AKA '
        # title += songs[song]['title']
        # hash = str(songs[song]['hash'])
        # imageInfo = {}
        # imageTypeToUse = 'album' if (songs[song]['show_thumb_url'] != '' and config['filter_song_thumbnail_type'] == 'show') else 'season' if (songs[song]['season_thumb_url'] != '' and config['filter_song_thumbnail_type'] == 'season') else 'song' if (songs[song]['user_thumb_url'] != '') else ''
        # print imageTypeToUse
        # if (imageTypeToUse == 'song'):
          # imageInfo['thumb'] = songs[song]['user_thumb_url']
          # imageInfo = processImage(hash, imageInfo['thumb'], 'episode', songs[song]['season_index'], songs[song]['index'])
        # elif (imageTypeToUse == 'album'):
          # imageInfo['thumb'] = songs[song]['season_thumb_url']
          # print songs[song]['season_thumb_url']
          # imageInfo = processImage(hash, imageInfo['thumb'], 'season', songs[song]['season_index'], 0)
        # elif (imageTypeToUse == 'artist'):
          # imageInfo['thumb'] = songs[song]['show_thumb_url']
          # imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
        
        # print imageInfo
        # print 
        # skipItem = False
        # emailText = ''
        # htmlText = ''
        # if (config['filter_include_plex_web_link']):
          # pwLink = plexWebLink + str(songs[song]['id'])
        # else:
          # pwLink = ''
      
        # emailText += '<table><tr width="100%">'
        # if (config['filter_show_email_images']):
          # emailText += '<td width="200"><a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></a></td>'
        # emailText += '<td><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + showTitle.decode('utf-8') + '</a></h2>'
        # emailText += '<p class="lead"><i>S' + str(songs[song]['season_index']) + ' E' + str(songs[song]['index']) + ': ' + title.decode('utf-8') + '</i></p>'
        # htmlText += '<div class="featurette" id="shows">'
        # htmlText += '<a target="_blank" href="' + pwLink + '"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px"></a>'
        # htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading"><a target="_blank" style="color: #000000;" href="' + pwLink + '">' + showTitle.decode('utf-8') + '</a></h2>'
        # htmlText += '<p class="lead"><i>S' + str(songs[song]['season_index']) + ' E' + str(songs[song]['index']) + ': ' + title.decode('utf-8') + '</i></p>'
        
        # sections = config['filter_sections_TV']
        # for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
          # if (songs[song][section[0]] in sections[section[0]]['exclude'] or len(set(songs[song][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and songs[song][section[0]] not in sections[section[0]]['include'] and len(set(songs[song][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
            # skipItem = True
          # if (sections[section[0]]['show'] and songs[song][section[0]] and songs[song][section[0]] != ''):
            # displayText = str(songs[song][section[0]])
            # if ('format' in sections[section[0]] and sections[section[0]]['format'] != ''):
              # displayText = time.strftime(sections[section[0]]['format'], time.strptime(displayText, '%Y-%m-%d %H:%M:%S'))
            # emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
            # htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + displayText.decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
        
        # emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
        # htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
        
        # titleFilter = []
        
        # if (songs[song]['show_title'] in config['filter_songs_exclude'] or len(set(titleFilter).intersection(config['filter_songs_exclude'])) > 0 or (config['filter_songs_include'] and songs[song]['show_title'] not in config['filter_songs_include'] and len(set(titleFilter).intersection(config['filter_songs_include'])) == 0)):
          # skipItem = True
        
        # if (not skipItem):
          # songCount += 1
          # emailSongs += emailText
          # htmlSongs += htmlText
    
    if ((movieCount > 0 and config['filter_show_movies']) or (showCount > 0 and config['filter_show_shows']) or (seasonCount > 0 and config['filter_show_seasons']) or (episodeCount > 0 and config['filter_show_episodes']) or (artistCount > 0 and config['filter_show_artists']) or (albumCount > 0 and config['filter_show_albums']) or (songCount > 0 and config['filter_show_songs'])):
      hasNewContent = True
    else:
      hasNewContent = False
    
    emailHTML = createEmailHTML()
    webHTML = createWebHTML()

    if (config['web_enabled'] and not config['web_only_save_images'] and (not config['web_skip_if_no_additions'] or hasNewContent)):
      with open(config['web_folder'] + config['web_path'] + os.path.sep + 'index.html', 'w') as text_file:
        text_file.write(webHTML.encode('utf-8'))
        print 'Web page created successfully'
    elif (not config['web_enabled'] or (config['web_only_save_images'] and config['web_enabled'])):
      print 'Web page was not created because the option is disabled in the config file.'
    else:
      print 'Web page was not created because there were no new additions in the timeframe specified.'
      
    if (config['email_enabled'] and (not config['email_skip_if_no_additions'] or hasNewContent)):
      # try:
      if (config['email_to_send_to_shared_users']):
        sharedEmails = getSharedUserEmails()
        config['email_to'].extend(x for x in sharedEmails if x not in config['email_to'])

      #Remove duplicates by converting to a set
      config['email_to'] = set(config['email_to'])
      
      emailCount = 0
      if (testMode):
        success = sendMail([config['email_from']])
        emailCount += success
      elif (config['email_individually']):
        for emailAdd in config['email_to']:
          email = [emailAdd]
          success = sendMail(email)
          emailCount += success
      else:
        success = sendMail('')
        emailCount += success
      print 'Successfully sent %s email(s)' % emailCount
      # except:
        # print "Failed to send email(s)"
    elif (not config['email_enabled']):
      print 'Emails were not sent because the option is disabled in the config file.'
    else:
      print 'Emails were not sent because there were no new additions in the timeframe specified.'
