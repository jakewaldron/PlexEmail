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
from base64 import b64encode
from collections import OrderedDict
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage
from email.header import Header
from email.utils import formataddr

def replaceConfigTokens():    
  ## The below code is for backwards compatibility
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
    
def convertToHumanReadable(valuesToConvert):
  convertedValues = {}
  for value in valuesToConvert:
    convertedValues[value] = valuesToConvert[value]
    convertedValues[value + '_filter'] = [valuesToConvert[value]]
    if (not valuesToConvert[value]):
      continue
    if (value == 'duration'):
      convertedValues[value] = str(valuesToConvert[value] // 1000 // 60)
    elif (value == 'rating'):
      convertedValues[value] = str(int(valuesToConvert[value] * 10))
    elif (value == 'tags_genre' or value == 'tags_star' or value == 'tags_director'):
      convertedValues[value + '_filter'] = valuesToConvert[value].split('|')
      convertedValues[value] = valuesToConvert[value].replace('|', ', ')
  return convertedValues

def deleteImages():
  folder = config['web_folder'] + config['web_path'] + os.path.sep + 'images' + os.path.sep
  for file in os.listdir(folder):
    if (file.endswith('.jpg')):
      os.remove(folder + file)
  
def processImage(imageHash, thumb, mediaType, seasonIndex, episodeIndex):
  thumbObj = {}
  if (not thumb or thumb == ''):
    thumbObj['webImgPath'] = ''
    thumbObj['emailImgPath'] = ''
    return thumbObj
    
  if (thumb.find('http://') >= 0):
    thumbObj['webImgPath'] = thumb
    thumbObj['emailImgPath'] = thumb  
  else:
    if (thumb.find('media://') >= 0):
      thumb = thumb[8:len(thumb)]
      imgName = thumb[thumb.rindex('/') + 1:thumb.rindex('.')] + hash
      imgLocation = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Media' + os.path.sep + 'localhost' + os.path.sep + '' + thumb
    elif (thumb.find('upload://') >= 0):
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
    
    cloudinaryURL = ''
    if ('upload_use_cloudinary' in config and config['upload_use_cloudinary']):
      thumbObj['emailImgPath'] = webImgFullPath
      #imgurURL = uploadToImgur(imgLocation, imgName)
      cloudinaryURL = uploadToCloudinary(imgLocation)
    elif (config['web_enabled'] and config['email_use_web_images']):
      thumbObj['emailImgPath'] = webImgFullPath
    elif (os.path.isfile(imgLocation)):
      imgNames['Image_' + imgName] = imgLocation
      thumbObj['emailImgPath'] = 'cid:Image_' + imgName
    else:
      thumbObj['emailImgPath'] = ''
      
    if (cloudinaryURL != ''):
      thumbObj['webImgPath'] = cloudinaryURL
      thumbObj['emailImgPath'] = cloudinaryURL
    elif (os.path.isfile(imgLocation) and config['web_enabled']):
      shutil.copy(imgLocation, img)
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
    print response
    print json.dumps(response.text)
    data = json.loads(response.text)['data'];
    return data['link']
  else:
    return ''
      
def uploadToCloudinary(imgToUpload):
  if (os.path.isfile(imgToUpload)):
    response = cloudinary.uploader.upload(imgToUpload)
    return response['url']
  else:
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
            
  if (movieCount > 0 and config['filter_show_movies']):
    emailText += emailMovies + '<br/>&nbsp;'
  if (showCount > 0 and config['filter_show_shows']):
    emailText += emailTVShows + '<br/>&nbsp;'
  if (seasonCount > 0 and config['filter_show_seasons']):
    emailText += emailTVSeasons + '<br/>&nbsp;'
  if (episodeCount > 0 and config['filter_show_episodes']):
    emailText += emailTVEpisodes
    
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
  
  if (movieCount > 0 and config['filter_show_movies']):
    htmlText += htmlMovies + '<br/>&nbsp;'
  if (showCount > 0 and config['filter_show_shows']):
    htmlText += htmlTVShows + '<br/>&nbsp;'
  if (seasonCount > 0 and config['filter_show_seasons']):
    htmlText += htmlTVSeasons + '<br/>&nbsp;'
  if (episodeCount > 0 and config['filter_show_episodes']):
    htmlText += htmlTVEpisodes
    
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

#
#
#  Main Code
#
#

parser = argparse.ArgumentParser(description='This script aggregates all new TV and movie releases for the past x days then writes to your web directory and sends out an email.')
parser.add_argument('-c','--configfile', help='The path to a config file to be used in the running of this instance of the script.', default=os.path.dirname(os.path.realpath(sys.argv[0])) + os.path.sep + 'config.conf', required=False)
parser.add_argument('-t','--test', help='Run this script in test mode - Sends email only to sender', action='store_true')
args = vars(parser.parse_args())

testMode = False
  
if ('configfile' in args):
  configFile = args['configfile']
if ('test' in args):
  testMode = args['test']

if (not os.path.isfile(configFile)):
  print configFile + ' does not exist'
  sys.exit()
  
config = {}
execfile(configFile, config)
replaceConfigTokens()

if ('upload_use_cloudinary' in config and config['upload_use_cloudinary']):
  cloudinary.config( 
    cloud_name = config['upload_cloudinary_cloud_name'],
    api_key = config['upload_cloudinary_api_key'],
    api_secret = config['upload_cloudinary_api_secret']
  )

DATABASE_FILE = config['plex_data_folder'] + 'Plex Media Server' + os.path.sep + 'Plug-in Support' + os.path.sep + 'Databases' + os.path.sep + 'com.plexapp.plugins.library.db'
  
if (not os.path.isfile(DATABASE_FILE)):
  print DATABASE_FILE + ' does not exist. Please make sure the plex_data_folder value is correct.'
  sys.exit()
  
con = sqlite3.connect(DATABASE_FILE)
con.text_factory = str

with con:
    libraryFilter = ''
    if (config['filter_libraries']):
      cur = con.cursor()
      cur.execute('SELECT id, name FROM library_sections;')
      for row in cur:
        if (row[1].lower() in (library.lower() for library in config['filter_libraries'])):
          if (libraryFilter == ''):
            libraryFilter = ' AND ('
            libraryFilter += 'library_section_id != ' + str(row[0])
          else:
            libraryFilter += ' OR library_section_id != ' + str(row[0])
      if (libraryFilter != ''):
        libraryFilter += ') '
      
    dateSearch = 'datetime(\'now\', \'localtime\', \'-' + str(config['date_days_back_to_search']) + ' days\', \'-' + str(config['date_hours_back_to_search']) + ' hours\', \'-' + str(config['date_minutes_back_to_search']) + ' minutes\')'

    cur = con.cursor()    
    cur.execute("SELECT id, parent_id, metadata_type, title, title_sort, original_title, rating, tagline, summary, content_rating, duration, user_thumb_url, tags_genre, tags_director, tags_star, year, hash, [index], studio FROM metadata_items WHERE added_at >= " + dateSearch + " AND metadata_type >= 1 AND metadata_type <= 4 " + libraryFilter + " ORDER BY title_sort;")

    response = {};
    for row in cur:
      response[row[0]] = {'id': row[0], 'parent_id': row[1], 'metadata_type': row[2], 'title': row[3], 'title_sort': row[4], 'original_title': row[5], 'rating': row[6], 'tagline': row[7], 'summary': row[8], 'content_rating': row[9], 'duration': row[10], 'user_thumb_url': row[11], 'tags_genre': row[12], 'tags_director': row[13], 'tags_star': row[14], 'year': row[15], 'hash': row[16], 'index': row[17], 'studio': row[18]}
            
    emailMovies = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_movies_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlMovies = """<hr class="featurette-divider" id="movies-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_movies_header'] + """</h2>
        </div>"""
    emailTVShows = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_shows_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVShows = """<hr class="featurette-divider" id="shows-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_shows_header'] + """</h2>
        </div>"""
    emailTVSeasons = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_seasons_header'] + """</font></h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVSeasons = """<hr class="featurette-divider" id="seasons-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">""" + config['msg_new_seasons_header'] + """</h2>
        </div>"""
    emailTVEpisodes = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important;"><font style="color: #F9AA03;">""" + config['msg_new_episodes_header'] + """</font></h1>
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
    movieCount = 0
    showCount = 0
    seasonCount = 0
    episodeCount = 0
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
      
      emailText += '<table><tr width="100%">'
      emailText += '<td width="200">'
      emailText += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154">'
      emailText += '</td>'
      emailText += '<td><h2 class="featurette-heading">' + title.decode('utf-8') + '</h2>'
      htmlText += '<div class="featurette" id="movies">'
      htmlText += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px">'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title.decode('utf-8') + '</h2>'
      
      sections = config['filter_sections_movies']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (movies[movie][section[0]] in sections[section[0]]['exclude'] or len(set(movies[movie][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and movies[movie][section[0]] not in sections[section[0]]['include'] and len(set(movies[movie][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
          skipItem = True
        if (sections[section[0]]['show'] and movies[movie][section[0]] and movies[movie][section[0]] != ''):
          emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(movies[movie][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
          htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(movies[movie][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
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
      
      emailText += '<table><tr width="100%">'
      emailText += '<td width="200"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></td>'
      emailText += '<td><h2 class="featurette-heading">' + title.decode('utf-8') + '</h2>'
      htmlText += '<div class="featurette" id="shows">'
      htmlText += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px">'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title.decode('utf-8') + '</h2>'      
      
      sections = config['filter_sections_TV']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (tvShows[show][section[0]] in sections[section[0]]['exclude'] or len(set(tvShows[show][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and tvShows[show][section[0]] not in sections[section[0]]['include'] and len(set(tvShows[show][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
          skipItem = True
        if (sections[section[0]]['show'] and tvShows[show][section[0]] and tvShows[show][section[0]] != ''):
          emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(tvShows[show][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
          htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(tvShows[show][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
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
      tvSeasons[season] = convertToHumanReadable(tvSeasons[season])
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
      
      skipItem = False
      emailText = ''
      htmlText = ''
      
      emailText += '<table><tr width="100%">'
      emailText += '<td width="200"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></td>'
      emailText += '<td><h2 class="featurette-heading">' + title.decode('utf-8') + '</h2>'
      emailText += '<p class="lead"><b>Season ' + str(tvSeasons[season]['index']) + '</b></p>'
      htmlText += '<div class="featurette" id="shows">'
      htmlText += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px">'
      htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title.decode('utf-8') + '</h2>'
      htmlText += '<p class="lead"><b>Season ' + str(tvSeasons[season]['index']) + '</b></p>'      
      
      sections = config['filter_sections_TV']
      for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
        if (tvSeasons[season][section[0]] in sections[section[0]]['exclude'] or len(set(tvSeasons[season][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and tvSeasons[season][section[0]] not in sections[section[0]]['include'] and len(set(tvSeasons[season][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
          skipItem = True
        if (sections[section[0]]['show'] and tvSeasons[season][section[0]] and tvSeasons[season][section[0]] != ''):
          emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(tvSeasons[season][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
          htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(tvSeasons[season][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
      
      emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
      
      if (not skipItem):
        seasonCount += 1
        emailTVSeasons += emailText
        htmlTVSeasons += htmlText
      
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
        tvEpisodes[episode] = convertToHumanReadable(tvEpisodes[episode])
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
        
        skipItem = False
        emailText = ''
        htmlText = ''
      
        emailText += '<table><tr width="100%">'
        emailText += '<td width="200"><img class="featurette-image img-responsive pull-left" src="' + imageInfo['emailImgPath'].decode('utf-8') +'" width="154"></td>'
        emailText += '<td><h2 class="featurette-heading">' + showTitle.decode('utf-8') + '</h2>'
        emailText += '<p class="lead"><i>S' + str(tvEpisodes[episode]['season_index']) + ' E' + str(tvEpisodes[episode]['index']) + ': ' + title.decode('utf-8') + '</i></p>'
        htmlText += '<div class="featurette" id="shows">'
        htmlText += '<img class="featurette-image img-responsive pull-left" src="' + imageInfo['webImgPath'].decode('utf-8') + '" width="154px" height="218px">'
        htmlText += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + showTitle.decode('utf-8') + '</h2>'
        htmlText += '<p class="lead"><i>S' + str(tvEpisodes[episode]['season_index']) + ' E' + str(tvEpisodes[episode]['index']) + ': ' + title.decode('utf-8') + '</i></p>'
        
        sections = config['filter_sections_TV']
        for section in sorted(sections.iteritems(), key=lambda t: t[1]['order']):
          if (tvEpisodes[episode][section[0]] in sections[section[0]]['exclude'] or len(set(tvEpisodes[episode][section[0] + '_filter']).intersection(sections[section[0]]['exclude'])) > 0 or (sections[section[0]]['include'] and tvEpisodes[episode][section[0]] not in sections[section[0]]['include'] and len(set(tvEpisodes[episode][section[0] + '_filter']).intersection(sections[section[0]]['include'])) == 0)):
            skipItem = True
          if (sections[section[0]]['show'] and tvEpisodes[episode][section[0]] and tvEpisodes[episode][section[0]] != ''):
            emailText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(tvEpisodes[episode][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
            htmlText += '<p class="lead">' + sections[section[0]]['preText'].decode('utf-8') + str(tvEpisodes[episode][section[0]]).decode('utf-8') + sections[section[0]]['postText'].decode('utf-8') + '</p>'
        
        emailText += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
        htmlText += '</div></div><br/>&nbsp;<br/>&nbsp;'
        
        if (not skipItem):
          episodeCount += 1
          emailTVEpisodes += emailText
          htmlTVEpisodes += htmlText

    if ((movieCount > 0 and config['filter_show_movies']) or (showCount > 0 and config['filter_show_shows']) or (seasonCount > 0 and config['filter_show_seasons']) or (episodeCount > 0 and config['filter_show_episodes'])):
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
      try:
        emailCount = 0
        if (testMode):
          sendMail([config['email_from']])
          emailCount += 1
        elif (config['email_individually']):
          for emailAdd in config['email_to']:
            email = [emailAdd]
            sendMail(email)
            emailCount += 1
        else:
          sendMail('')
          emailCount += 1
        print 'Successfully sent %s email(s)' % emailCount
      except:
        print "Failed to send email(s)"
    elif (not config['email_enabled']):
      print 'Emails were not sent because the option is disabled in the config file.'
    else:
      print 'Emails were not sent because there were no new additions in the timeframe specified.'