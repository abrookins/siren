from fabric import api


DEPLOY_DIR = '/home/andrew/apps/siren'


@api.task
@api.hosts('andrew@andrewbrookins.com')
def deploy():
    api.local('git push origin master')

    with api.cd(DEPLOY_DIR):
       api.run('touch app.wsgi')
