"""
Assumptions:
    You will use SSH keys to access to the one system account. ``DEPLOY``
    You have one github account for private projects.
    You name the github project the same as the website.

The Deploy Machine will create following folder for each website:
    ``/var/www/sitename/``

Inside of this folder, Deploy Machine will checkout your github project of
the same exact name, and inside the top level of that project, it expects to
find the following structure.

    ``/var/www/sitename/sitemame/.git``
    ``/var/www/sitename/sitemame/manage.py``
    ``/var/www/sitename/sitemame/settings.py``
    ``/var/www/sitename/sitemame/settings_local.py``
    ``/var/www/sitename/sitemame/requirements.txt``

Roles are:
    loadbalancer, appnode, dbserver,
    appbalancer (combined loadbalancer and appnode)
    dbappbalancer (combined loadbalancer, appnode, dbserver)

Flavors:
    +----+---------------+-------+------+
    | ID |      Name     |  RAM  | Disk |
    +----+---------------+-------+------+
    | 1  | 256 server    | 256   | 10   |
    | 2  | 512 server    | 512   | 20   |
    | 3  | 1GB server    | 1024  | 40   |
    | 4  | 2GB server    | 2048  | 80   |
    | 5  | 4GB server    | 4096  | 160  |
    | 6  | 8GB server    | 8192  | 320  |
    | 7  | 15.5GB server | 15872 | 620  |
    +----+---------------+-------+------+
"""

# Options "kokki", puppet", "chef"
CONFIGURATORS = ["chef", "kokki", "puppet"]
# DeployMachine would have fewer lines of code and a little less complex if it
# ran all commands as root, but taking the extra precaution of requiring sudo
# authentication for all commands post provision will be worth the added effort.
DEPLOY_USERNAME = "deploy"
# It is first necessary to encrypt the password with a unique password and salt:
    #perl -e "print crypt('D3pl0YM@c4In3', '1k8u')"
DEPLOY_PASSWORD_RAW = "D3pl0YM@c4In3"
DEPLOY_PASSWORD = "1kHr.Jjj7EqAM"

DEPLOY_MACHINE_ROOT = "/var/www/lib/deploymachine"
SCENE_MACHINE_ROOT = "/var/www/lib/django-scene-machine/scene-machine"
PINAX_ROOT = "/var/www/lib/pinax/pinax"

GITHUB_USERNAME = "me"
GITHUB_TOKEN = "@@@"
DOTFILE_REPOSITORY = "git://github.com/rizumu/deploymachine-dotfiles.git"

CUMULUS_USERNAME = "me"
CUMULUS_API_KEY = "@@@"
CUMULUS_DEFAULT_IMAGE_ID = 69
CLOUDSERVERS = {"appnode": [("finnegan", "1")]}
PUPPETMASTER = "finnegan" # Name of puppetmaster machiene

# @@@ Eventually auto build a custom python version, ie 2.5, 2.6, 2.7.1
PYTHON_VERSION = "2.6" #Distro's python version
PINAX_VERSION = "0.9a2.dev10"

# Change the default SSH port of 22
SSH_PORT = "30000"
# The following core packages are essential, only append core packages here.
# Non-core packages to be installed via a configurationa management recipe.
BASE_PACKAGES = [
    "build-essential",
    "git-core",
    "libjpeg62",
    "libjpeg62-dev",
    "libyaml-0-2",
    "libyaml-dev",
    "mercurial",
    "python-dev",
    "python-yaml",
]
# The names of the public key files for users who should have SSH access
# Place these files in the ssh/ folder of ``DEPLOY_MACHINE_ROOT``
ADMIN_SSH_KEYS = [
    "me.pub",
    "you.pub",
    "her.pub",
]
# Websites: {websitename} must be the same as the project on github.
# ex. github.com/{username}/{websitename}/.git
# Top level directory in the repo must also be the django project's PROJECT_ROOT,
# It must contain the settings.py, urls.py, requirements.txt files and
# apps/ templates/ static/ folders.
SITES = [
    "djangoproject",
    "rtfd",
    "pycon",
]
# PostgreSQL is assumed.
# Choose a database port and necessary databases.
# Probably needs to be set in your configuration management tool's config too.
PGSQL_PORT = 60000
#"dbname": "password",
DATABASES = {
    "db_1": "password",
    "db_2": "drowssap",
}
