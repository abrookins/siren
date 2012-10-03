from fabric import api


DEPLOY_DIR = '/home/andrew/apps/siren'


@api.task
@api.hosts('andrew@andrewbrookins.com')
def deploy(install_reqs=False):
    api.local('git push origin master')

    with api.cd(DEPLOY_DIR):
       api.run('git pull origin master')

       if install_reqs:
           api.run('export WORKON_HOME=~/envs && source virtualenvwrapper.sh '
                   '&& workon siren && pip install -r requirements.txt')

       api.sudo('supervisorctl restart siren')
