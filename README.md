Plex Email
==========

## Introduction
This script aggregates all new TV and movie releases for the past x days and writes to your web directory and sends out an email.

## Supported Environments
* Windows - Tested
* Linux - Tested
* Mac - Tested

## Supported Email Protocols
* SMTP

## Prerequisites

1. Python 2.7 - Windows: 32 bit - https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi
2. Windows - 32 bit DLL for SQLite version 3.8.8.3 - http://www.sqlite.org/2015/sqlite-dll-win32-x86-3080803.zip (Put this into the DLLs folder of the Python installation)
3. Requests module for Python. pip install requests or download it here and put it in the LIb folder of your Python installation: https://pypi.python.org/packages/source/r/requests/requests-2.5.3.tar.gz#md5=23bf4fcc89ea8d353eb5353bb4a475b1
4. If web reports are wanted, a web server (i.e. Wamp, Apache, etc.)


## Installation (Windows)

1. Clone this repo or download the zip
2. Copy the contents of scripts to where you want the script to run from
3. Copy the contents of web to your web folder
4. Update the config.conf file inside the scripts folder
5. Schedule a weekly task to execute plexEmail.vbs from the scripts folder (make sure to set the start in folder as the folder where the vbs script resides)

## Installation (Linux)

1. Install python 2.7.9
2. Copy the contents of scripts to where you want the script to run from
3. Copy the contents of web to your web folder
4. Update the config.conf file inside the scripts folder
5. Schedule a weekly cron job to execute the plexEmail.py script

## Installation (CentOS)

https://forums.plex.tv/index.php/topic/151619-plexemail-in-development/page-7#entry879778

## Usage

#### Normal Usage

```
python plexEmail.py
```

#### Alternate Usage

Pass in an alternate config file.  For example the default config file sends out a daily email (using Cloudinary), while an alternate config file is set up for a weekly web page.

```
python plexEmail.py -c C:\files\plexEmailWeekly.conf
```

Run in test mode (send email only to sender address)

```
python plexEmail.py -t
```

Pass a special one-time notice to users

```
python plexEmail.py -n "This is a special notice to all users"
```

## Config File

The config file is in the scripts folder.  Before first run of the script, please update this file with your information.

####Field Explanations:

#####Folder Paths
* plex_data_folder - Location where the Plex Media Server folder is located - i.e. E:\\Library\\Plex\\
* web_folder - Location of web/www/public_html folder is located - i.e. C:\\wamp\\www\\

#####General
* date_format - Format to use for the date
* date_days_back_to_search - Number of days to search backwards
* date_hours_back_to_search - Number of hours to search backwards
* date_minutes_back_to_search - Number of minutes to search backwards

#####Plex API Authentication - This is only used for shared user emails currently
* plex_username - Plex account username of the server
* plex_password - Plex account password of the server

#####Web
* web_enabled - Enable the creation of the web page
* web_domain - Domain name of the web page
* web_path - Path on the domain to the web page
* web_delete_previous_images - True to delete all .jpg images in the web image folder prior to copying over current images
* web_skip_if_no_additions - True to skip creating a web page if there are no new additions

#####Image Upload - If this option is enabled, image hosting will be used for web and email

##Cloudinary - Sign up for a free account at: http://cloudinary.com/
* upload_use_cloudinary - Use Cloudinary image hosting
* upload_cloudinary_cloud_name - Cloudinary cloud name
* upload_cloudinary_api_key - Cloudinary api key
* upload_cloudinary_api_secret - Cloudinary api secret

#####Email
* email_enabled - Enable the creation and sending of an email
* email_individually - True to send out emails individually to each address in the email_to setting
* email_use_bcc - True to send emails on using bcc instead of to (email_to settings will send to them using bcc)
* email_to - Array of email addresses to send the email
* email_to_send_to_shared_users - True to get list of shared user emails (plex_username and plex_password must be valid for this to be used)
* email_from - Email address to send the email from
* email_from_name - Friendly name of sender
* email_smtp_address - SMTP address of the email service
* email_smtp_port - SMTP port of the email service
* email_use_ssl - Use SSL - Note that the port must be an SSL port for this to work i.e. 465
* email_username - SMTP authentication username
* email_password - SMTP authentication password
* email_use_web_images - Use images from the web server instead of attaching them directly to the email
* email_skip_if_no_additions - True to skip sending emails if there are no new additions

#####Filtering
* filter_include_plex_web_link - True to add hyperlinks to the images and titles to go to Plex Web for the specific title
* filter_show_movies - True to show recently added movies
* filter_show_shows - True to show recently added TV shows
* filter_show_seasons - True to show recently added TV seasons
* filter_show_episodes - True to show recently added TV episodes
* filter_show_email_images - True to show images in the email
* filter_libraries - A list of library names to filter out - ['Home Videos', 'Private']
* filter_sections_movies - Movie specific filters
* filter_sections_TV - TV specific filters
  * Possible fields: tagline, summary, content_rating, duration, year, rating, studio, tags_genre, tags_director, tags_star
  * order - The order this field should appear for each title
  * show - Whether or not this field should be shown for each title
  * preText - The text that should be added before this field for each title
  * postText - The text that should be added after this field for each title
  * include - A list of values that are each title must match at least one to be shown
  * exclude - A list of values that if the title matches any of, will not be shown

#####Messages
* msg_notice - Used for special notices to the users. This can also be done through the command line using the -n flag.
* msg_email_teaser - Teaser text on the email
* msg_web_title - Title of the webpage
* msg_email_subject Subject of email
* msg_header1 - First header text
* msg_header2 - Second header text
* msg_header3 - Third header text.  Only used in the email
* msg_top_link - Header link text to go to top of the page
* msg_movies_link - Header link text to go to new movies
* msg_shows_link - Header link text to go to new shows
* msg_seasons_link - Header link text to go to new seasons
* msg_episodes_link - Header link text to go to new episodes
* msg_new_movies_header - Section header text for new movies
* msg_new_shows_header - Section header text for new shows
* msg_new_seasons_header - Section header text for new seasons
* msg_new_episodes_header - Section header text for new episodes
* msg_footer - Footer text at the bottom of the page
* msg_no_new_content - Message to be displayed if no new content has been added

#####Sorting
* movie_sort_1 - Highest priority sort
* movie_sort_1_reverse - Reverse the default sort
* movie_sort_2 - Second priority sort
* movie_sort_2_reverse - Reverse the default sort
* movie_sort_3 - Third Priority sort
* movie_sort_3_reverse - Reverse the default sort

* show_sort_1 - Highest priority sort
* show_sort_1_reverse - Reverse the default sort
* show_sort_2 - Second priority sort
* show_sort_2_reverse - Reverse the default sort
* show_sort_3 - Third Priority sort
* show_sort_3_reverse - Reverse the default sort

* season_sort_1 - Highest priority sort
* season_sort_1_reverse - Reverse the default sort
* season_sort_2 - Second priority sort
* season_sort_2_reverse - Reverse the default sort
* season_sort_3 - Third Priority sort
* season_sort_3_reverse - Reverse the default sort

* episode_sort_1 - Highest priority sort
* episode_sort_1_reverse - Reverse the default sort
* episode_sort_2 - Second priority sort
* episode_sort_2_reverse - Reverse the default sort
* episode_sort_3 - Third Priority sort
* episode_sort_3_reverse - Reverse the default sort

## Screenshots

### Email

Top:
![alt tag](http://i.imgur.com/ufWQcw8.png)

Movies:
![alt tag](http://i.imgur.com/jf5QKKL.png)

TV Shows:
![alt tag](http://i.imgur.com/CalJ2b8.png)

TV Seasons:
![alt tag](http://i.imgur.com/tqMqGVa.png)

TV Episodes:
![alt tag](http://i.imgur.com/zujePDP.png)

### Web

Top:
![alt tag](http://i.imgur.com/eRikpyh.png)

Movies:
![alt tag](http://i.imgur.com/nZIyg36.png)

TV Shows:
![alt tag](http://i.imgur.com/cY36zCz.png)

TV Seasons:
![alt tag](http://i.imgur.com/fF7HNL4.jpg)

TV Episodes:
![alt tag](http://i.imgur.com/xiwUNPT.jpg)
