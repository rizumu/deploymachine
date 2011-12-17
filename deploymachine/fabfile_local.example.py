# scenemachine specific
from fabric.api import cd, env, local, sudo

import deploymachine_settings as settings

from deploymachine.contrib import django, fab, git, supervisor


def deploy_git_rizumu():
    git.pull("rizumu")
    git.pull_scenemachine()
    django.staticfiles("rizumu")
    supervisor.restart("rizumu")


def git_pull_sceneachine():
    with cd(settings.SCENEMACHINE_ROOT):
        sudo("git pull", user=env.user)


def git_pull_pinax():
    with cd(settings.PINAX_ROOT):
        sudo("git pull", user=env.user)


def dump_data_rizumu():
    venv("python manage.py dumpdata --format=yaml --indent=4 --natural \
          events people music places hyperlinks > ../../dumps/sitedump.yaml", "rizumu")


def loaddata_sites(connection):
    if connection == 'dev':
        venv_local("python manage.py loaddata\
        /home/deploy/www/lib/scenemachine/scenemachine/fixtures/sites/site_data.yaml", "smus")
    elif connection == "prod":
        venv("python manage.py loaddata\
        /home/deploy/www/lib/scenemachine/scenemachine/fixtures/sites/site_data.yaml", "smus")
    else:
        print("Bad connection type. Use ``dev`` or ``prod``.")


def full_deploy(static=False):
    """
    Full scenemachine deploy
    Usage:
        fab appbalancer full_deploy:static=True

    Remember to handle requirements separately.
    """
    git_pull_scenemachine()
    settings_local("prod")
    git.pull()
    if static:
        django.staticfiles()
    supervisor.restart()
