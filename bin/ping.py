#!/usr/bin/env python

import urllib2

# Ping the site every 10 minutes, to make sure Heroku doesn't spin it down.
resp = urllib2.urlopen(
    'http://pdxcrime.herokuapp.com/crime/stats/45.6159782376,-122.690757299')
