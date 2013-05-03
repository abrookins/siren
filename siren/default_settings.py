import os


BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))

CACHE_TYPE = 'filesystem'
CACHE_THRESHOLD = 1000
CACHE_DIR = os.path.join(BASE_DIR, 'cache')

DATA_DIR = os.path.join(BASE_DIR, 'data')
