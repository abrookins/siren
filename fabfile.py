from fabric import api

@api.task
def deploy(sync_media=True):
    api.local('git push heroku master')

    if sync_media:
        api.local('s3cmd sync public/ s3://pdxcrime.org/')
