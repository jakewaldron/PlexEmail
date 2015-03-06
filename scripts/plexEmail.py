import sqlite3
import sys
import os
import json
import operator
import shutil
import smtplib
from datetime import date, timedelta

def replaceConfigTokens():
  for value in config:
    if (isinstance(config[value], str)):
      config[value] = config[value].replace('{past_day}', str((date.today() - timedelta(days=config['days_back_to_search'])).strftime(config['date_format'])))
      config[value] = config[value].replace('{current_day}', str(date.today().strftime(config['date_format'])))
      config[value] = config[value].replace('{website}', config['web_domain'] + config['web_path'])
    
config = {}
execfile(os.path.dirname(os.path.realpath(sys.argv[0])) + '\\config.conf', config)
replaceConfigTokens()

DATABASE_FILE = config['plex_data_folder'] + 'Plex Media Server\\Plug-in Support\\Databases\\com.plexapp.plugins.library.db'
  
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
                        <a class="navbar-brand" href="#">What's New in Plex</a>
                    </div>
                    <!-- Collect the nav links, forms, and other content for toggling -->
                    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                        <ul class="nav navbar-nav">
                            <li>
                                <a href="#movies-top">Movies</a>
                            </li>
                            <li>
                                <a href="#shows-top">TV Shows</a>
                            </li>
                            <li>
                                <a href="#seasons-top">TV Seasons</a>
                            </li>
                            <li>
                                <a href="#episodes-top">TV Episodes</a>
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
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New Movies</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlMovies = """<hr class="featurette-divider" id="movies-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New Movies</h2>
        </div>"""
    emailTVShows = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New TV Shows</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVShows = """<hr class="featurette-divider" id="shows-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New TV Shows</h2>
        </div>"""
    emailTVSeasons = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New TV Seasons</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVSeasons = """<hr class="featurette-divider" id="seasons-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New TV Seasons</h2>
        </div>"""
    emailTVEpisodes = """<div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h1 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New TV Episodes</h1>
        </div><hr class="featurette-divider" id="movies-top"><br/>&nbsp;"""
    htmlTVEpisodes = """<hr class="featurette-divider" id="episodes-top">
    <div class="headline" style="background: #FFF !important; padding-top: 0px !important;">
          <h2 style="width: 100%; text-align: center; background: #FFF !important; color: #F9AA03 !important;">New TV Episodes</h2>
        </div>"""
    movies = {}
    tvShows = {}
    tvSeasons = {}
    tvEpisodes = {}
    imgNames = {}
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
    
    for movie in (sorted(movies.items(), key=lambda t: (t[1]['rating'], t[1]['title_sort']), reverse=True)):
      title = ''
      if (movie[1]['original_title'] != ''):
        title += movie[1]['original_title'] + ' AKA '
      title += movie[1]['title']
      hash = str(movie[1]['hash'])
      thumb = movie[1]['user_thumb_url']
      if (thumb.find('http://') < 0):
        thumb = thumb[11:len(thumb)]
        category = thumb[0:thumb.index('/')]
        indexer = thumb[thumb.index('/') + 1:thumb.index('_')]
        imgName = thumb[thumb.index('_') + 1:len(thumb)]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\Movies\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\' + category + '\\' + imgName
        webImgPath = 'images/' + imgName + '.png'
        webImgFullPath = config['web_domain'] + config['web_path'] + '/images/' + imgName + '.png'
        emailImgPath = 'cid:Image_' + imgName
        img = config['web_folder'] + config['web_path'] + '\\images\\' + imgName + '.png'
        shutil.copy(imgLocation, img)
        if (config['web_enabled'] == False or config['email_use_web_images'] == False):
          imgNames['Image_' + imgName] = imgLocation
      else:
        imgName = thumb[thumb.rfind('/') + 1:thumb.rfind('.')]
        imgLocation = thumb
        webImgPath = thumb
        webImgFullPath = thumb
        emailImgPath = thumb
        
      if (config['web_enabled'] and config['email_use_web_images']):
        emailImgPath = webImgFullPath
      
      emailMovies += '<table><tr width="100%">'
      emailMovies += '<td width="200px">'
      if (imgName != ''):
        emailMovies += '<img class="featurette-image img-responsive pull-left" src="' + emailImgPath +'" width="154px">'
      emailMovies += '</td>'
      emailMovies += '<td><h2 class="featurette-heading">' + title + '</h2>'
      if (movie[1]['tagline'] != ''):
        emailMovies += '<p class="lead"><i>' + movie[1]['tagline'] + '</i></p>'
      emailMovies += '<p class="lead">' + movie[1]['summary'] + '</p>'
      if (movie[1]['duration']):
        emailMovies += '<p class="lead">Runtime: ' + str(movie[1]['duration'] // 1000 // 60) + ' minutes</p>'
      if (movie[1]['year']):
        emailMovies += '<p class="lead">Release Year: ' + str(movie[1]['year']) + '</p>'
      if (movie[1]['rating']):
        emailMovies += '<p class="lead">Rating: ' + str(int(movie[1]['rating'] * 10)) + '%</p>'
      emailMovies += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      
      htmlMovies += '<div class="featurette" id="movies">'
      htmlMovies += '<img class="featurette-image img-responsive pull-left" src="' + webImgPath + '" width="154px" height="218px">'
      htmlMovies += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title + '</h2>'
      if (movie[1]['tagline'] != ''):
        htmlMovies += '<p class="lead"><i>' + movie[1]['tagline'] + '</i></p>'
      htmlMovies += '<p class="lead">' + movie[1]['summary'] + '</p>'
      if (movie[1]['duration']):
        htmlMovies += '<p class="lead">Runtime: ' + str(movie[1]['duration'] // 1000 // 60) + ' minutes</p>'
      if (movie[1]['year']):
        htmlMovies += '<p class="lead">Release Year: ' + str(movie[1]['year']) + '</p>'
      if (movie[1]['rating']):
        htmlMovies += '<p class="lead">Rating: ' + str(int(movie[1]['rating'] * 10)) + '%</p>'
      htmlMovies += '</div></div><br/>&nbsp;<br/>&nbsp;'
    
    for show in (sorted(tvShows.items(), key=lambda t: (t[1]['title_sort']))):
      title = ''
      if (show[1]['original_title'] != ''):
        title += show[1]['original_title'] + ' AKA '
      title += show[1]['title']
      hash = str(show[1]['hash'])
      thumb = show[1]['user_thumb_url']
      if (thumb.find('http://') < 0):
        thumb = thumb[11:len(thumb)]
        category = thumb[0:thumb.index('/')]
        indexer = thumb[thumb.index('/') + 1:thumb.index('_')]
        imgName = thumb[thumb.index('_') + 1:len(thumb)]
        imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\TV Shows\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\' + category + '\\' + imgName
        webImgPath = 'images/' + imgName + '.png'
        webImgFullPath = config['web_domain'] + config['web_path'] + '/images/' + imgName + '.png'
        emailImgPath = 'cid:Image_' + imgName
        img = config['web_folder'] + config['web_path'] + '\\images\\' + imgName + '.png'
        shutil.copy(imgLocation, img)
        if (config['web_enabled'] == False or config['email_use_web_images'] == False):
          imgNames['Image_' + imgName] = imgLocation
      else:
        imgName = thumb[thumb.rfind('/') + 1:thumb.rfind('.')]
        imgLocation = thumb
        webImgPath = thumb
        webImgFullPath = thumb
        emailImgPath = thumb
        
      if (config['web_enabled'] and config['email_use_web_images']):
        emailImgPath = webImgFullPath
      
      emailTVShows += '<table><tr width="100%">'
      emailTVShows += '<td width="200px"><img class="featurette-image img-responsive pull-left" src="' + emailImgPath +'" width="154px"></td>'
      emailTVShows += '<td><h2 class="featurette-heading">' + title + '</h2>'
      if (show[1]['tagline'] != ''):
        emailTVShows += '<p class="lead"><i>' + show[1]['tagline'] + '</i></p>'
      emailTVShows += '<p class="lead">' + show[1]['summary'] + '</p>'
      if (show[1]['studio'] != ''):
        emailTVShows += '<p class="lead">Network: ' + show[1]['studio'] + '</p>'
      emailTVShows += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      
      htmlTVShows += '<div class="featurette" id="shows">'
      htmlTVShows += '<img class="featurette-image img-responsive pull-left" src="' + webImgPath + '" width="154px" height="218px">'
      htmlTVShows += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title + '</h2>'
      if (show[1]['tagline'] != ''):
        htmlTVShows += '<p class="lead"><i>' + show[1]['tagline'] + '</i></p>'
      htmlTVShows += '<p class="lead">' + show[1]['summary'] + '</p>'
      if (show[1]['studio'] != ''):
        htmlTVShows += '<p class="lead">Network: ' + show[1]['studio'] + '</p>'
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
          
    for season in (sorted(tvSeasons.items(), key=lambda t: (t[1]['title_sort'], t[1]['index']))):
      title = ''
      if (season[1]['original_title'] != ''):
        title += season[1]['original_title'] + ' AKA '
      title += season[1]['title']
      hash = str(season[1]['hash'])
      thumb = season[1]['user_thumb_url']
      if (thumb == ''):
        thumb = season[1]['parent_thumb_url']
      if (thumb.find('http://') < 0):
        thumb = thumb[11:len(thumb)]
        category = thumb[0:thumb.index('/')]
        indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
        imgName = thumb[thumb.index('_') + 1:len(thumb)]
        if (season[1]['user_thumb_url'] != ""):
          imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\TV Shows\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\' + category + '\\' + str(season[1]['index']) + '\\posters\\' + imgName
        else:
          imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\TV Shows\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\' + category + '\\' + imgName
        webImgPath = 'images/' + imgName + '.png'
        webImgFullPath = config['web_domain'] + config['web_path'] + '/images/' + imgName + '.png'
        emailImgPath = 'cid:Image_' + imgName
        img = config['web_folder'] + config['web_path'] + '\\images\\' + imgName + '.png'
        shutil.copy(imgLocation, img)
        if (config['web_enabled'] == False or config['email_use_web_images'] == False):
          imgNames['Image_' + imgName] = imgLocation
      else:
        imgName = thumb[thumb.rfind('/') + 1:thumb.rfind('.')]
        imgLocation = thumb
        webImgPath = thumb
        webImgFullPath = thumb
        emailImgPath = thumb
        
      if (config['web_enabled'] and config['email_use_web_images']):
        emailImgPath = webImgFullPath
      
      emailTVSeasons += '<table><tr width="100%">'
      emailTVSeasons += '<td width="200px"><img class="featurette-image img-responsive pull-left" src="' + emailImgPath +'" width="154px"></td>'
      emailTVSeasons += '<td><h2 class="featurette-heading">' + title + '</h2>'
      emailTVSeasons += '<p class="lead"><b>Season ' + str(season[1]['index']) + '</b></p>'
      if (season[1]['tagline'] != ''):
        emailTVSeasons += '<p class="lead"><i>' + season[1]['tagline'] + '</i></p>'
      emailTVSeasons += '<p class="lead">' + season[1]['summary'] + '</p>'
      if (season[1]['studio'] != ''):
        emailTVSeasons += '<p class="lead">Network: ' + season[1]['studio'] + '</p>'
      emailTVSeasons += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
      
      htmlTVSeasons += '<div class="featurette" id="shows">'
      htmlTVSeasons += '<img class="featurette-image img-responsive pull-left" src="' + webImgPath + '" width="154px" height="218px">'
      htmlTVSeasons += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + title + '</h2>'
      htmlTVSeasons += '<p class="lead"><b>Season ' + str(season[1]['index']) + '</b></p>'
      if (season[1]['tagline'] != ''):
        htmlTVSeasons += '<p class="lead"><i>' + season[1]['tagline'] + '</i></p>'
      htmlTVSeasons += '<p class="lead">' + season[1]['summary'] + '</p>'
      if (season[1]['studio'] != ''):
        htmlTVSeasons += '<p class="lead">Network: ' + season[1]['studio'] + '</p>'
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
          
    for episode in (sorted(tvEpisodes.items(), key=lambda t: (t[1]['show_title_sort'], t[1]['season_index'], t[1]['index']))):
      if (episode[1]['parent_id'] not in tvSeasons):
        showTitle = ''
        if (episode[1]['show_original_title'] != ''):
          showTitle += episode[1]['show_original_title'] + ' AKA '
        showTitle += episode[1]['show_title']
        title = ''
        if (episode[1]['original_title'] != ''):
          title += episode[1]['original_title'] + ' AKA '
        title += episode[1]['title']
        hash = str(episode[1]['hash'])
        thumb = episode[1]['user_thumb_url']
        if (thumb == ''):
          thumb = episode[1]['season_thumb_url']
        if (thumb == ''):
          thumb = episode[1]['show_thumb_url']
        if (thumb.find('http://') < 0):
          if (episode[1]['user_thumb_url'] != "" and 'metadata://' in episode[1]['user_thumb_url']):
            thumb = episode[1]['user_thumb_url']
            thumb = thumb[11:len(thumb)]
            category = thumb[0:thumb.index('/')]
            indexer = thumb[thumb.index('thumbs/') + 7:thumb.index('_')]
            imgName = thumb[thumb.index('_') + 1:len(thumb)]
            imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\TV Shows\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\seasons\\' + str(episode[1]['season_index']) + '\\episodes\\' + str(episode[1]['index']) + '\\thumbs\\' + imgName
          elif (episode[1]['season_thumb_url'] != ""):
            thumb = episode[1]['season_thumb_url']
            thumb = thumb[11:len(thumb)]
            category = thumb[0:thumb.index('/')]
            indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
            imgName = thumb[thumb.index('_') + 1:len(thumb)]
            imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\TV Shows\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\seasons\\' + str(episode[1]['season_index']) + '\\posters\\' + imgName
          else:
            thumb = episode[1]['show_thumb_url']
            thumb = thumb[11:len(thumb)]
            category = thumb[0:thumb.index('/')]
            indexer = thumb[thumb.index('posters/') + 8:thumb.index('_')]
            imgName = thumb[thumb.index('_') + 1:len(thumb)]
            imgLocation = config['plex_data_folder'] + 'Plex Media Server\\Metadata\\TV Shows\\' + hash[0] + '\\' + hash[1:len(hash)] + '.bundle\\Contents\\' + indexer + '\\' + category + '\\' + imgName
          webImgPath = 'images/' + imgName + '.png'
          webImgFullPath = config['web_domain'] + config['web_path'] + '/images/' + imgName + '.png'
          emailImgPath = 'cid:Image_' + imgName
          img = config['web_folder'] + config['web_path'] + '\\images\\' + imgName + '.png'
          shutil.copy(imgLocation, img)
          if (config['web_enabled'] == False or config['email_use_web_images'] == False):
            imgNames['Image_' + imgName] = imgLocation
        else:
          imgName = thumb[thumb.rfind('/') + 1:thumb.rfind('.')]
          imgLocation = thumb
          webImgPath = thumb
          webImgFullPath = thumb
          emailImgPath = thumb

        if (config['web_enabled'] and config['email_use_web_images']):
          emailImgPath = webImgFullPath
        
        emailTVEpisodes += '<table><tr width="100%">'
        emailTVEpisodes += '<td width="200px"><img class="featurette-image img-responsive pull-left" src="' + emailImgPath +'" width="154px"></td>'
        emailTVEpisodes += '<td><h2 class="featurette-heading">' + showTitle + '</h2>'
        emailTVEpisodes += '<p class="lead"><i>S' + str(episode[1]['season_index']) + ' E' + str(episode[1]['index']) + ': ' + title + '</i></p>'
        if (episode[1]['tagline'] != ''):
          emailTVEpisodes += '<p class="lead"><i>' + episode[1]['tagline'] + '</i></p>'
        emailTVEpisodes += '<p class="lead">' + episode[1]['summary'] + '</p>'
        if (episode[1]['studio'] != ''):
          emailTVEpisodes += '<p class="lead">Network: ' + episode[1]['studio'] + '</p>'
        emailTVEpisodes += '</td></tr></table><br/>&nbsp;<br/>&nbsp;'
        
        htmlTVEpisodes += '<div class="featurette" id="shows">'
        htmlTVEpisodes += '<img class="featurette-image img-responsive pull-left" src="' + webImgPath + '" width="154px" height="218px">'
        htmlTVEpisodes += '<div style="margin-left: 200px;"><h2 class="featurette-heading">' + showTitle + '</h2>'
        htmlTVEpisodes += '<p class="lead"><i>S' + str(episode[1]['season_index']) + ' E' + str(episode[1]['index']) + ': ' + title + '</i></p>'
        if (episode[1]['tagline'] != ''):
          htmlTVEpisodes += '<p class="lead"><i>' + episode[1]['tagline'] + '</i></p>'
        htmlTVEpisodes += '<p class="lead">' + episode[1]['summary'] + '</p>'
        if (episode[1]['studio'] != ''):
          htmlTVEpisodes += '<p class="lead">Network: ' + episode[1]['studio'] + '</p>'
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
	
    if (config['web_enabled']):
      with open(config['web_folder'] + config['web_path'] + '\\index.html', 'w') as text_file:
        text_file.write(html)
      
    if (config['email_enabled']):
      from email.mime.multipart import MIMEMultipart
      from email.mime.text import MIMEText
      from email.MIMEImage import MIMEImage
      
      gmail_user = config['email_username']
      gmail_pwd = config['email_password']
      smtp_address = config['email_smtp_address']
      smtp_port = config['email_smtp_port']
      FROM = config['email_from']
      TO = config['email_to']
      SUBJECT = config['msg_email_subject']
      TEXT = emailText

      # Create message container - the correct MIME type is multipart/alternative.
      msg = MIMEMultipart('alternative')
      msg['Subject'] = SUBJECT
      msg['From'] = FROM
      msg['To'] = ", ".join(TO)

      # Create the body of the message (a plain-text and an HTML version).
      text = config['msg_email_teaser']

      # Record the MIME types of both parts - text/plain and text/html.
      part1 = MIMEText(text, 'plain')
      part2 = MIMEText(emailText, 'html')
      
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
      msg.attach(part1)
      msg.attach(part2)

      try:
          #server = smtplib.SMTP(SERVER) 
          server = smtplib.SMTP(smtp_address, smtp_port) #or port 465 doesn't seem to work!
          server.ehlo()
          server.starttls()
          server.login(gmail_user, gmail_pwd)
          server.sendmail(FROM, TO, msg.as_string())
          #server.quit()
          server.close()
          print 'successfully sent the mail'
      except:
          print "failed to send mail"