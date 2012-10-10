from fabric import api


@api.task
def push():
    api.local('git push origin master')


@api.task
def deploy_app():
    api.local('git push heroku master')


@api.task
def sync_media(force=False):
    s3cmd = 'put' if force else 'sync'
    api.local(
        's3cmd %s --acl-public --recursive public/ s3://pdxcrime.org/' % s3cmd)


@api.task
def deploy(sync=True, force=False):
    """
    Deploy to Heroku and put or sync assts to S3.

    TODO: Render templates/index.html and save outpu to public/index.html, so
    we can configure the API server per-deploy.
    """
    api.execute(deploy_app)
    if sync:
        api.execute(sync_media, force=force)
