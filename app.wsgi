import os
import site
import sys

project_dir = os.path.dirname(os.path.realpath(__file__))

site.addsitedir('/home/andrew/envs/siren/lib/python2.6/site-packages')
sys.path.append(project_dir)

from siren import app as application

