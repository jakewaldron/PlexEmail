import sqlite3
import sys
import os
import json
import operator
import shutil
import smtplib
from collections import OrderedDict
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage
from email.header import Header
from email.utils import formataddr

def replaceConfigTokens():
  for value in config:
    if (isinstance(config[value], str)):
      config[value] = config[value].replace('{past_day}', str((date.today() - timedelta(days=config['days_back_to_search'])).strftime(config['date_format'])))
      config[value] = config[value].replace('{current_day}', str(date.today().strftime(config['date_format'])))
      config[value] = config[value].replace('{website}', config['web_domain'] + config['web_path'])
      config[value] = config[value].replace('{path_sep}', os.path.sep)

  if (config['plex_data_folder'] and config['plex_data_folder'].rfind(os.path.sep) < len(config['plex_data_folder']) - len(os.path.sep)):
    config['plex_data_folder'] = config['plex_data_folder'] + os.path.sep
    
  if (config['web_folder'] and config['web_folder'].rfind(os.path.sep) < len(config['web_folder']) - len(os.path.sep)):
    config['web_folder'] = config['web_folder'] + os.path.sep
    
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

def deleteImages():
  folder = config['web_folder'] + config['web_path'] + os.path.sep + 'images' + os.path.sep
  for file in os.listdir(folder):
    print folder, file
    if (file.endswith('.jpg')):
      os.remove(folder + file)
  
def processImage(imageHash, thumb, mediaType, seasonIndex, episodeIndex):
  thumbObj = {}
  if (thumb.find('http://') >= 0):
    thumbObj['webImgPath'] = thumb
    thumbObj['emailImgPath'] = thumb  
  else:
    if (thumb.find('media://') >= 0):
      thumb = thumb[7:len(thumb)]
      imgName = thumb[thumb.rindex('/') + 1:thumb.rindex('.')] + hash
      imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Media' + os.path.sep + 'localhost' + os.path.sep + '' + thumb
    else:
      thumb = thumb[11:len(thumb)]
      category = thumb[0:thumb.index('/')]
      imgName = thumb[thumb.index('_') + 1:len(thumb)]
      if (mediaType == 'movie'):
        indexer = thumb[thumb.index('/') + 1:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'Movies' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + indexer + os.path.sep + category + os.path.sep + imgName
      elif (mediaType == 'show'):
        indexer = thumb[thumb.index('/') + 1:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'TV Shows' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + indexer + os.path.sep + category + os.path.sep + imgName
      elif (mediaType == 'season'):
        indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'TV Shows' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + indexer + os.path.sep + 'seasons' + os.path.sep + str(seasonIndex) + os.path.sep + 'posters' + os.path.sep + imgName
      elif (mediaType == 'episode'):
        indexer = thumb[thumb.index('thumbs/') + 7:thumb.index('_')]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Metadata' + os.path.sep + 'TV Shows' + os.path.sep + imageHash[0] + os.path.sep + imageHash[1:len(imageHash)] + '.bundle' + os.path.sep + 'Contents' + os.path.sep + indexer + os.path.sep + 'seasons' + os.path.sep + str(seasonIndex) + os.path.sep + 'episodes' + os.path.sep + str(episodeIndex) + os.path.sep + 'thumbs' + os.path.sep + imgName
    webImgFullPath = config['web_domain'] + config['web_path'] + '/images/' + imgName + '.jpg'
    img = config['web_folder'] + config['web_path'] + os.path.sep + 'images' + os.path.sep + imgName + '.jpg'
      
    if (config['web_enabled'] and config['email_use_web_images']):
      thumbObj['emailImgPath'] = webImgFullPath
    elif (os.path.isfile(imgLocation)):
      imgNames['Image_' + imgName] = imgLocation
      thumbObj['emailImgPath'] = 'cid:Image_' + imgName
      
    if (os.path.isfile(imgLocation)):
      shutil.copy(imgLocation, img)
      thumbObj['webImgPath'] = 'images/' + imgName + '.jpg'
    else:
      thumbObj['webImgPath'] = ''
      thumbObj['emailImgPath'] = ''
    
  return thumbObj
        
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
  gmail_user = config['email_username']
  gmail_pwd = config['email_password']
  smtp_address = config['email_smtp_address']
  smtp_port = config['email_smtp_port']
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
  if containsnonasciicharacters(emailText):
    htmltext = MIMEText(emailText, 'html','utf-8')
  else:
    htmltext = MIMEText(emailText, 'html')    

  if(containsnonasciicharacters(text)):
    plaintext = MIMEText(text,'plain','utf-8') 
  else:
    plaintext = MIMEText(text,'plain')
  
  #Create image headers
  for image in imgNames:
    fp = open(imgNames[image], 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<' + image + '>')
    msg.attach(msgImage)

  # Attach parts into message container.
  # According to RFC 2046, the last part of a multipart message, in this case
  # the HTML message, is best and preferred.
  msg.attach(plaintext)
  msg.attach(htmltext)
  msg['To'] = ", ".join(TO)
  server = smtplib.SMTP(smtp_address, smtp_port) #or port 465 doesn't seem to work!
  server.ehlo()
  server.starttls()
  server.login(gmail_user, gmail_pwd)
  server.sendmail(FROM, TO, msg.as_string())
  server.close()
    
config = {}
execfile(os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep + 'config.conf', config)
replaceConfigTokens()

DATABASE_FILE = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Plug-in Support' + os.path.sep + 'Databases' + os.path.sep + 'com.plexapp.plugins.library.db'
  
con = sqlite3.connect(DATABASE_FILE)
con.text_factory = str

with con:    
    
    cur = con.cursor()    
    cur.execute("SELECT id, parent_id, metadata_type, title, title_sort, original_title, rating, tagline, summary, content_rating, duration, user_thumb_url, tags_genre, tags_director, tags_star, year, hash, [index], studio FROM metadata_items WHERE added_at >= date('now', '-" + str(config['days_back_to_search']) + " days') AND metadata_type >= 1 AND metadata_type <= 4 ORDER BY title_sort;")

    response = {};
    for row in cur:
        response[row[0]] = {'id': row[0], 'parent_id': row[1], 'metadata_type': row[2], 'title': row[3], 'title_sort': row[4], 'original_title': row[5], 'rating': row[6], 'tagline': row[7], 'summary': row[8], 'content_rating': row[9], 'duration': row[10], 'user_thumb_url': row[11], 'tags_genre': row[12], 'tags_director': row[13], 'tags_star': row[14], 'year': row[15], 'hash': row[16], 'index': row[17], 'studio': row[18]}
    
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
            <header class="header-image" style="background: #272727;">
                <div class="headline" style="background: #272727;  padding: 40px 0;">
                    <div class="container" style="background: #272727;">
                        <h1 style="width: 100%; text-align: center; background: #272727 !important; color: #F9AA03 !important;">""" + config['msg_header1'] + """</h1>
                        <h2 style="width: 100%; text-align: center; background: #272727 !important; color: #9A9A9A !important;">""" + config['msg_header2'] + """</h2>
                        <h2 style="width: 100%; text-align: center; background: #272727 !important; color: #9A9A9A !important;">""" + config['msg_header3'] + """</h2>
                </div>
                </div>
            </header>

            <!-- Page Content -->
            <div class="container">"""

    html = """<!DOCTYPE html>
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
                        <ul class="nav navbar-nav">
                            <li>
                                <a href="#movies-top">""" + config['msg_movies_link'] + """</a>
                            </li>
                            <li>
                                <a href="#shows-top">""" + config['msg_shows_link'] + """</a>
                            </li>
                            <li>
                                <a href="#seasons-top">""" + config['msg_seasons_link'] + """</a>
                            </li>
                            <li>
                                <a href="#episodes-top">""" + config['msg_episodes_link'] + """</a>
                            </li>
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
            
    emailMovies = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_movies_header'] + """</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlMovies = """<hr class="featurette-divider" id="movies-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_movies_header'] + """</h2>
        </div>"""
    emailTVShows = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_shows_header'] + """</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVShows = """<hr class="featurette-divider" id="shows-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_shows_header'] + """</h2>
        </div>"""
    emailTVSeasons = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_seasons_header'] + """</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVSeasons = """<hr class="featurette-divider" id="seasons-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_seasons_header'] + """</h2>
        </div>"""
    emailTVEpisodes = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_episodes_header'] + """</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVEpisodes = """<hr class="featurette-divider" id="episodes-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_episodes_header'] + """</h2>
        </div>"""
    movies = {}
    tvShows = {}
    tvSeasons = {}
    tvEpisodes = {}
    imgNames = {}
    if (config['web_enabled'] and 'web_delete_previous_images' in config and config['web_delete_previous_images']):
      deleteImages()
    for item in response:
      #Handle New Movies
      if (response[item]['metadata_type'] == 1):
        movies[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 2):
        tvShows[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 3):
        tvSeasons[response[item]['id']] = response[item]
      
      if (response[item]['metadata_type'] == 4):
        tvEpisodes[response[item]['id']] = response[item]
        
    if ('movie_sort_3' in config and config['movie_sort_3'] != ''):
      movies = OrderedDict(sorted(movies.iteritems(), key=lambda t: t[1][config['movie_sort_3']], reverse=config['movie_sort_3_reverse']))
    if ('movie_sort_2' in config and config['movie_sort_2'] != ''):
      movies = OrderedDict(sorted(movies.iteritems(), key=lambda t: t[1][config['movie_sort_2']], reverse=config['movie_sort_2_reverse']))
    if ('movie_sort_1' in config and config['movie_sort_1'] != ''):
      movies = OrderedDict(sorted(movies.iteritems(), key=lambda t: t[1][config['movie_sort_1']], reverse=config['movie_sort_1_reverse']))
    
    for movie in movies:
      title = ''
      if (movies[movie]['original_title'] != ''):
        title += movies[movie]['original_title'] + ' AKA '
      title += movies[movie]['title']
      hash = str(movies[movie]['hash'])
      imageInfo = {}
      imageInfo['thumb'] = movies[movie]['user_thumb_url']
      imageInfo = processImage(hash, imageInfo['thumb'], 'movie', 0, 0)
      
      emailMovies += '<table><tr width="100%">'
      emailMovies += '<td width="200px">'
      emailMovies += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'] +'" width="154px">'
      emailMovies += '</td>'
      emailMovies += '<td><h2 class="featurette-heading">' + title + '</h2>'
      if (movies[movie]['tagline'] != ''):
        emailMovies += '<p class="lead"><i>' + movies[movie]['tagline'] + '</i></p>'
      emailMovies += '<p class="lead">' + movies[movie]['summary'] + '</p>'
      if (movies[movie]['duration']):
        emailMovies += '<p class="lead">Runtime: ' + str(movies[movie]['duration'] // 1000 // 60) + ' minutes</p>'
      if (movies[movie]['year']):
        emailMovies += '<p class="lead">Release Year: ' + str(movies[movie]['year']) + '</p>'
      if (movies[movie]['rating']):
        emailMovies += '<p class="lead">Rating: ' + str(int(movies[movie]['rating'] * 10)) + '%</p>'
      emailMovies += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      
      htmlMovies += '<div class="featurette" id="movies">'
      htmlMovies += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'] + '" width="154px" height="218px">'
      htmlMovies += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title + '</h2>'
      if (movies[movie]['tagline'] != ''):
        htmlMovies += '<p class="lead"><i>' + movies[movie]['tagline'] + '</i></p>'
      htmlMovies += '<p class="lead">' + movies[movie]['summary'] + '</p>'
      if (movies[movie]['duration']):
        htmlMovies += '<p class="lead">Runtime: ' + str(movies[movie]['duration'] // 1000 // 60) + ' minutes</p>'
      if (movies[movie]['year']):
        htmlMovies += '<p class="lead">Release Year: ' + str(movies[movie]['year']) + '</p>'
      if (movies[movie]['rating']):
        htmlMovies += '<p class="lead">Rating: ' + str(int(movies[movie]['rating'] * 10)) + '%</p>'
      htmlMovies += '</div></div><br/>&nbsp;<br/>&nbsp;'
    
    if ('show_sort_3' in config and config['show_sort_3'] != ''):
      tvShows = OrderedDict(sorted(tvShows.iteritems(), key=lambda t: t[1][config['show_sort_3']], reverse=config['show_sort_3_reverse']))
    if ('show_sort_2' in config and config['show_sort_2'] != ''):
      tvShows = OrderedDict(sorted(tvShows.iteritems(), key=lambda t: t[1][config['show_sort_2']], reverse=config['show_sort_2_reverse']))
    if ('show_sort_1' in config and config['show_sort_1'] != ''):
      tvShows = OrderedDict(sorted(tvShows.iteritems(), key=lambda t: t[1][config['show_sort_1']], reverse=config['show_sort_1_reverse']))
    
    for show in tvShows:
      title = ''
      if (tvShows[show]['original_title'] != ''):
        title += tvShows[show]['original_title'] + ' AKA '
      title += tvShows[show]['title']
      hash = str(tvShows[show]['hash'])
      imageInfo = {}
      imageInfo['thumb'] = tvShows[show]['user_thumb_url']
      imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
      
      emailTVShows += '<table><tr width="100%">'
      emailTVShows += '<td width="200px"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'] +'" width="154px"></td>'
      emailTVShows += '<td><h2 class="featurette-heading">' + title + '</h2>'
      if (tvShows[show]['tagline'] != ''):
        emailTVShows += '<p class="lead"><i>' + tvShows[show]['tagline'] + '</i></p>'
      emailTVShows += '<p class="lead">' + tvShows[show]['summary'] + '</p>'
      if (tvShows[show]['studio'] != ''):
        emailTVShows += '<p class="lead">Network: ' + tvShows[show]['studio'] + '</p>'
      emailTVShows += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      
      htmlTVShows += '<div class="featurette" id="shows">'
      htmlTVShows += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'] + '" width="154px" height="218px">'
      htmlTVShows += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title + '</h2>'
      if (tvShows[show]['tagline'] != ''):
        htmlTVShows += '<p class="lead"><i>' + tvShows[show]['tagline'] + '</i></p>'
      htmlTVShows += '<p class="lead">' + tvShows[show]['summary'] + '</p>'
      if (tvShows[show]['studio'] != ''):
        htmlTVShows += '<p class="lead">Network: ' + tvShows[show]['studio'] + '</p>'
      htmlTVShows += '</div></div><br/>&nbsp;<br/>&nbsp;'
    
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
        tvSeasons[season]['hash'] = row[12]
        tvSeasons[season]['parent_thumb_url'] = row[13]
        tvSeasons[season]['studio'] = row[14]
          
    if ('season_sort_3' in config and config['season_sort_3'] != ''):
      tvSeasons = OrderedDict(sorted(tvSeasons.iteritems(), key=lambda t: t[1][config['season_sort_3']], reverse=config['season_sort_3_reverse']))
    if ('season_sort_2' in config and config['season_sort_2'] != ''):
      tvSeasons = OrderedDict(sorted(tvSeasons.iteritems(), key=lambda t: t[1][config['season_sort_2']], reverse=config['season_sort_2_reverse']))
    if ('season_sort_1' in config and config['season_sort_1'] != ''):
      tvSeasons = OrderedDict(sorted(tvSeasons.iteritems(), key=lambda t: t[1][config['season_sort_1']], reverse=config['season_sort_1_reverse']))
    
    for season in tvSeasons:
      title = ''
      if (tvSeasons[season]['original_title'] != ''):
        title += tvSeasons[season]['original_title'] + ' AKA '
      title += tvSeasons[season]['title']
      hash = str(tvSeasons[season]['hash'])
      imageInfo = {}
      if (tvSeasons[season]['user_thumb_url'] != ''):
        imageInfo['thumb'] = tvSeasons[season]['user_thumb_url']
        imageInfo = processImage(hash, imageInfo['thumb'], 'season', tvSeasons[season]['index'], 0)
      else:
        imageInfo['thumb'] = tvSeasons[season]['parent_thumb_url']
        imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
      
      emailTVSeasons += '<table><tr width="100%">'
      emailTVSeasons += '<td width="200px"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'] +'" width="154px"></td>'
      emailTVSeasons += '<td><h2 class="featurette-heading">' + title + '</h2>'
      emailTVSeasons += '<p class="lead"><b>Season ' + str(tvSeasons[season]['index']) + '</b></p>'
      if (tvSeasons[season]['tagline'] != ''):
        emailTVSeasons += '<p class="lead"><i>' + tvSeasons[season]['tagline'] + '</i></p>'
      emailTVSeasons += '<p class="lead">' + tvSeasons[season]['summary'] + '</p>'
      if (tvSeasons[season]['studio'] != ''):
        emailTVSeasons += '<p class="lead">Network: ' + tvSeasons[season]['studio'] + '</p>'
      emailTVSeasons += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      
      htmlTVSeasons += '<div class="featurette" id="shows">'
      htmlTVSeasons += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'] + '" width="154px" height="218px">'
      htmlTVSeasons += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title + '</h2>'
      htmlTVSeasons += '<p class="lead"><b>Season ' + str(tvSeasons[season]['index']) + '</b></p>'
      if (tvSeasons[season]['tagline'] != ''):
        htmlTVSeasons += '<p class="lead"><i>' + tvSeasons[season]['tagline'] + '</i></p>'
      htmlTVSeasons += '<p class="lead">' + tvSeasons[season]['summary'] + '</p>'
      if (tvSeasons[season]['studio'] != ''):
        htmlTVSeasons += '<p class="lead">Network: ' + tvSeasons[season]['studio'] + '</p>'
      htmlTVSeasons += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
    for episode in tvEpisodes:
      cur2 = con.cursor()
      cur2.execute("SELECT user_thumb_url, parent_id, [index] FROM metadata_items WHERE id = " + str(tvEpisodes[episode]['parent_id']) + ";")

      for row in cur2:
        tvEpisodes[episode]['season_thumb_url'] = row[0]
        parent_id = row[1]
        tvEpisodes[episode]['season_index'] = row[2]
        
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
          tvEpisodes[episode]['hash'] = row2[7]
          tvEpisodes[episode]['show_thumb_url'] = row2[8]
          tvEpisodes[episode]['studio'] = row2[9]
          
    if ('episode_sort_3' in config and config['episode_sort_3'] != ''):
      tvEpisodes = OrderedDict(sorted(tvEpisodes.iteritems(), key=lambda t: t[1][config['episode_sort_3']], reverse=config['episode_sort_3_reverse']))
    if ('episode_sort_2' in config and config['episode_sort_2'] != ''):
      tvEpisodes = OrderedDict(sorted(tvEpisodes.iteritems(), key=lambda t: t[1][config['episode_sort_2']], reverse=config['episode_sort_2_reverse']))
    if ('episode_sort_1' in config and config['episode_sort_1'] != ''):
      tvEpisodes = OrderedDict(sorted(tvEpisodes.iteritems(), key=lambda t: t[1][config['episode_sort_1']], reverse=config['episode_sort_1_reverse']))
    
    for episode in tvEpisodes:
      if (tvEpisodes[episode]['parent_id'] not in tvSeasons):
        showTitle = ''
        if (tvEpisodes[episode]['show_original_title'] != ''):
          showTitle += tvEpisodes[episode]['show_original_title'] + ' AKA '
        showTitle += tvEpisodes[episode]['show_title']
        title = ''
        if (tvEpisodes[episode]['original_title'] != ''):
          title += tvEpisodes[episode]['original_title'] + ' AKA '
        title += tvEpisodes[episode]['title']
        hash = str(tvEpisodes[episode]['hash'])
        imageInfo = {}
        if (tvEpisodes[episode]['user_thumb_url'] != ''):
          imageInfo['thumb'] = tvEpisodes[episode]['user_thumb_url']
          imageInfo = processImage(hash, imageInfo['thumb'], 'episode', tvEpisodes[episode]['season_index'], tvEpisodes[episode]['index'])
        elif (tvEpisodes[episode]['season_thumb_url'] != ''):
          imageInfo['thumb'] = tvEpisodes[episode]['season_thumb_url']
          imageInfo = processImage(hash, imageInfo['thumb'], 'season', tvEpisodes[episode]['season_index'], 0)
        elif (tvEpisodes[episode]['show_thumb_url'] != ''):
          imageInfo['thumb'] = tvEpisodes[episode]['show_thumb_url']
          imageInfo = processImage(hash, imageInfo['thumb'], 'show', 0, 0)
        
        emailTVEpisodes += '<table><tr width="100%">'
        emailTVEpisodes += '<td width="200px"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'] +'" width="154px"></td>'
        emailTVEpisodes += '<td><h2 class="featurette-heading">' + showTitle + '</h2>'
        emailTVEpisodes += '<p class="lead"><i>S' + str(tvEpisodes[episode]['season_index']) + ' E' + str(tvEpisodes[episode]['index']) + ': ' + title + '</i></p>'
        if (tvEpisodes[episode]['tagline'] != ''):
          emailTVEpisodes += '<p class="lead"><i>' + tvEpisodes[episode]['tagline'] + '</i></p>'
        emailTVEpisodes += '<p class="lead">' + tvEpisodes[episode]['summary'] + '</p>'
        if (tvEpisodes[episode]['studio'] != ''):
          emailTVEpisodes += '<p class="lead">Network: ' + tvEpisodes[episode]['studio'] + '</p>'
        emailTVEpisodes += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
        
        htmlTVEpisodes += '<div class="featurette" id="shows">'
        htmlTVEpisodes += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'] + '" width="154px" height="218px">'
        htmlTVEpisodes += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + showTitle + '</h2>'
        htmlTVEpisodes += '<p class="lead"><i>S' + str(tvEpisodes[episode]['season_index']) + ' E' + str(tvEpisodes[episode]['index']) + ': ' + title + '</i></p>'
        if (tvEpisodes[episode]['tagline'] != ''):
          htmlTVEpisodes += '<p class="lead"><i>' + tvEpisodes[episode]['tagline'] + '</i></p>'
        htmlTVEpisodes += '<p class="lead">' + tvEpisodes[episode]['summary'] + '</p>'
        if (tvEpisodes[episode]['studio'] != ''):
          htmlTVEpisodes += '<p class="lead">Network: ' + tvEpisodes[episode]['studio'] + '</p>'
        htmlTVEpisodes += '</div></div><br/>&nbsp;<br/>&nbsp;'
    
    emailText += emailMovies + '<br/>&nbsp;' + emailTVShows + '<br/>&nbsp;' + emailTVSeasons + '<br/>&nbsp;' + emailTVEpisodes + """
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
    
    html += htmlMovies + '<br/>&nbsp;' + htmlTVShows + '<br/>&nbsp;' + htmlTVSeasons + '<br/>&nbsp;' + htmlTVEpisodes + """<hr class="featurette-divider">

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
	
    if (config['web_enabled']):
      with open(config['web_folder'] + config['web_path'] + os.path.sep + 'index.html', 'w') as text_file:
        text_file.write(html)
      
    if (config['email_enabled']):      
      try:
        emailCount = 0
        if (config['email_individually']):
          for emailAdd in config['email_to']:
            email = [emailAdd]
            sendMail(email)
            emailCount += 1
        else:
          sendMail('')
          emailCount += 1
        print 'successfully sent %s email(s)' % emailCount
      except:
        print "failed to send email"