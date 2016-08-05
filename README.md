django-liveplaylist
===================

LivePlaylist is a reusable app written in python to manage your livestreams and provide an
up-to-date playlist for i.e. your TVHeadend instance (IPTV auto network).

Overview
========

-   Create HTML-Scrapers to scrape a Webpage and look there (in subpages) for public playists
-   Create SourceWrappers to make use of i.e. livestreamer and ffmpeg and pipe your stream as TS to TVHeadend
    -   see live-Script in demodata
    -   To use this script install livestreamer and ffmpeg at your TVHeadend server, make the script executable
        test it
-   Manage your own stream sources (LiveSource)

Installation
============

in a virtualenv:

    virtualenv liveplvenv
    cd liveplvenv
    source bin/activate
    pip install django requests lxml

    mkdir src
    cd src
    git clone https://bitbucket.org/ckarrie/django-liveplaylist
    pip install -e django-liveplaylist

now setup up your django projects to your needs (settings.py) and add/set following settings:

    INSTALLED_APPS += ['liveplaylist']

django-playlist comes with a predefined urls config:

    ROOT_URLS = 'liveplaylist.urls'

install the demo data, but don't forget to create a superuser first (manage.py createsuperuser) with id = 1

    manage.py loaddata ~/liveplvenv/src/django-liveplaylist/demodata/liveplaylist.json

Update your Playlist
====================

create a CRON-job to update your PlaylistUpdate instance every hour:

    0   *    *   *   *   /<pathtovenv>/bin/python /<pathtodjangoproject>/manage.py update_playlists > update_playlists.log


Live-Test
=========

    User: demo
    Password: --tvheadendisthebest--