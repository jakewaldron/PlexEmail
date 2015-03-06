Plex Email
==========

## Introduction
This script aggregates all new TV and movie releases for the past x days and writes to your web directory and sends out an email.

## Supported Environments
* Windows

## Supported Email Protocols
* SMTP

## Prerequisites

1. Python 2.7 - 32 bit - https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi
2. 32 bit DLL for SQLite version 3.8.8.3 - http://www.sqlite.org/2015/sqlite-dll-win32-x86-3080803.zip (Put this into the DLLs folder of the Python installation)
3. If web reports are wanted, a web server (i.e. Wamp)


## Installation (Windows)

1. Clone this repo or download the zip
2. Copy the contents of scripts to where you want the script to run from
3. Copy the contents of web to your web folder
4. Schedule a weekly task to exectute scripts\plexEmail.vbs (make sure to set the start in folder as the folder where the vbs script resides)

## Config File

The config file is in the scripts folder.  Before first run of the script, please update this file with your information.

####Required Fields to Update:

* plex_data_folder
* web_folder
* web_domain
* web_path
* email_to
* email_from
* email_smtp_address (gmail default)
* email_smtp_port
* email_username
* email_password

####Field Explanations:

#####Folder Paths
* plex_data_folder - Location where the Plex Media Server folder is located - i.e. E:\\Library\\Plex\\
* web_folder - Location of web/www/public_html folder is located - i.e. C:\\wamp\\www\\

#####General
* date_format - Format to use for the date
* days_back_to_search - Number of days to search backwards

#####Messages
* msg_email_teaser - Teaser text on the email
* msg_web_title - Title of the webpage
* msg_email_subject Subject of email
* msg_header1 - First header text
* msg_header2 - Second header text
* msg_header3 - Third header text.  Only used in the email

#####Web
* web_enabled - Enable the creation of the web page
* web_domain - Domain name of the web page
* web_path - Path on the domain to the web page

#####Email
* email_enabled - Enable the creation and sending of an email
* email_to - Array of email addresses to send the email
* email_from - Email address to send the email from
* email_smtp_address - SMTP address of the email service
* email_smtp_port - SMTP port of the email service
* email_username - SMTP authentication username
* email_password - SMTP authentication password

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
