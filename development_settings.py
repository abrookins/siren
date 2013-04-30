import os

DEBUG = True

CACHE_TYPE = 'filesystem'
CACHE_THRESHOLD = 1000
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
