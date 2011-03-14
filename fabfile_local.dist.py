from fabric.api import cd, env, local, sudo

from deploymachine.conf import settings
from deploymachine.fablib.django import collectstatic, settings_local
from deploymachine.fablib.dvcs.git import git_pull, git_pull_deploy_machine
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.fab import venv, venv_local


# rizumu specific
def deploy_git_rizumu():
    git_pull("rizumu")
    git_pull_scene_machine()
    collectstatic("rizumu")
    supervisor("rizumu")


def git_pull_scene_machine():
    with cd(settings.SCENE_MACHINE_ROOT):
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
        /var/www/lib/django-scene-machine/scene-machine/fixtures/sites/site_data.yaml", "smus")
    elif connection == "prod":
        venv("python manage.py loaddata\
        /var/www/lib/django-scene-machine/scene-machine/fixtures/sites/site_data.yaml", "smus")
    else:
        print("Bad connection type. Use ``dev`` or ``prod``.")


def full_deploy(collectstatic=False):
    """
    Full scenemachine deploy
    Usage:
        fab appbalancer full_deploy:collectstatic=True

    Remember to handle requirements separately.
    """
    git_pull_deploy_machine()
    git_pull_scene_machine()
    settings_local("prod")
    git_pull()
    if collectstatic:
        collectstatic()

def symlinks(connection, site=None):
    """
    Link pinax & pydiscogs into the virtualenv's site-packages.
    @@@ this is hardcoded ugliness
    Usage:
        fab appnode symlinks:prod,sitename
    """
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    if connection == "dev":
        for site in site_list:
            try:
                local("ln -sf /var/www/lib/pinax/pinax ~/.virtualenvs/{0}/lib/python2.7/site-packages/pinax".format(site))
                local("ln -sf /var/www/lib/pydiscogs/pydiscogs ~/.virtualenvs/{0}/lib/python2.7/site-packages/pydiscogs".format(site))
            except:
                local("ln -sf /var/www/lib/pinax/pinax ~/.virtualenvs/{0}/lib/python2.6/site-packages/pinax".format(site))
                local("ln -sf /var/www/lib/pydiscogs/pydiscogs ~/.virtualenvs/{0}/lib/python2.6/site-packages/pydiscogs".format(site))
            local("ln -sf /var/www/lib/deploy-machine/fabfile.py /var/www/{0}/{0}/fabfile.py".format(site))
            local("ln -sf /var/www/lib/deploy-machine/settings.py /var/www/{0}/{0}/settings.py".format(site))
            local("ln -sf /var/www/lib/deploy-machine/dmfab /var/www/{0}/{0}/dmfab".format(site))
        local("ln -sf /var/www/lib/deploy-machine/fabfile.py /var/www/lib/django-scene-machine/fabfile.py".format(site))
        local("ln -sf /var/www/lib/deploy-machine/settings.py /var/www/lib/django-scene-machine/settings.py".format(site))
        local("ln -sf /var/www/lib/deploy-machine/dmfab /var/www/lib/django-scene-machine/dmfab".format(site))
    elif connection == "prod":
        for site in site_list:
            with cd("/home/deploy/.virtualenvs/{0}/lib/python{1}/site-packages".format(site, env.python_version)):
                sudo("ln -sf /var/www/lib/pinax/pinax", user="deploy")
                sudo("ln -sf /var/www/lib/pydiscogs/pydiscogs".format(settings.PINAX_ROOT), user="deploy")
    else:
        print("Bad connection type. Use ``dev`` or ``prod``.")

