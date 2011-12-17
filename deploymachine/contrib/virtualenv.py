import os

from fabric.api import cd, env, lcd, local, sudo, put, run
from fabric.contrib.files import append, contains, exists
from fabric.decorators import task

import deploymachine_settings as settings
from deploymachine.contrib.pip import pip_install, pip_requirements, pip_uninstall


@task
def generate_virtualenv(connection, site=None, python_bin="python"):
    """
    Creates or rebuilds a site's virtualenv.
    @@@TODO muliple envs for one site, aka predictable rollbacks.
    Usage:
        fab generate_virtualenv:dev,sitename
        fab appnode generate_virtualenv:prod,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        if connection == "dev" and not contains("{0}{1}".format(settings.SITES_ROOT, "virtualenv_dev.log"), site):
            log_name = "virtualenv_dev.log"
            local("rm -rf {0}{1}/".format(settings.VIRTUALENVS_LOCAL_ROOT, site))
            with lcd(settings.VIRTUALENVS_LOCAL_ROOT):
                local("virtualenv --no-site-packages --distribute --python={0} {1}".format(python_bin, site))
            with lcd("{0}{1}".format(settings.SITES_LOCAL_ROOT, site)):
                local("ln -sf {0}{1}/lib/python{2}/site-packages".format(settings.VIRTUALENVS_LOCAL_ROOT, site, settings.PYTHON_VERSION))
            local("echo 'cd {0}{1}/{1}' >> {2}{1}/bin/postactivate".format(settings.SITES_LOCAL_ROOT, site, settings.VIRTUALENVS_LOCAL_ROOT))
            symlink_packages("dev", site)
            pip_requirements("dev", site)
        elif connection == "prod" and not contains("{0}{1}".format(settings.SITES_ROOT, "virtualenv_prod.log"), site):
            log_name = "virtualenv_prod.log"
            run("rm -rf {0}{1}/".format(settings.VIRTUALENVS_ROOT, site))
            with cd(settings.VIRTUALENVS_ROOT):
                run("virtualenv --no-site-packages --distribute {0}".format(site))
            if not exists("{0}{1}/site-packages".format(settings.SITES_ROOT, site)):
                with cd("{0}{1}".format(settings.SITES_ROOT, site)):
                    run("ln -sf {0}{1}/lib/python{2}/site-packages".format(settings.VIRTUALENVS_ROOT, site, settings.PYTHON_VERSION))
            append("{0}{1}/bin/postactivate".format(settings.VIRTUALENVS_ROOT, site),
                   "{0}{1}/{1}".format(settings.SITES_ROOT, site,))
            symlink_packages("prod", site)
            pip_requirements("prod", site)
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")
        append("{0}{1}".format(settings.SITES_ROOT, log_name), site)
        print(green("sucessfully built virtualenv for for {0}".format(site)))
    run("rm {0}{1}".format(settings.SITES_ROOT, "virtualenv.log"))
    print(green("sucessfully built virtualenvs for all sites!".format(site)))


@task
def symlink_packages(connection, site=None):
    """
    Hook to add symlinks into the virtualenv's site-package for
    personal libraries which aren't on pypi and therefore not in
    requirements.
    @@@ Define these packages in ``settings_deploymachine.py``.
    Usage:
        fab appnode symlink_packages:prod,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        if connection == "dev":
            site_packages = os.path.join(settings.VIRTUALENVS_LOCAL_ROOT, site,
                                         "lib/python{0}/".format(settings.PYTHON_VERSION),
                                         "site-packages/")
            with lcd(site_packages):
                local("ln -sf {0}".format(settings.SCENEMACHINE_LOCAL_ROOT[:-1]))
                local("ln -sf {0}".format(settings.DEPLOYMACHINE_LOCAL_ROOT[:-1]))
                #local("ln -sf {0}".format(settings.PYDISCOGS_LOCAL_ROOT[:-1]))
        elif connection == "prod":
            site_packages = os.path.join(settings.VIRTUALENVS_ROOT, site,
                                         "lib/python{0}/".format(settings.PYTHON_VERSION),
                                         "site-packages/")
            with cd(site_packages):
                run("ln -sf {0}".format(settings.PINAX_ROOT))
                run("ln -sf {0}".format(settings.SCENEMACHINE_ROOT))
                #run("ln -sf {0}".format(settings.PYDISCOGS_ROOT[:-1]))
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")
