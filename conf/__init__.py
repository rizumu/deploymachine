# @@@ this is dumb, but makes for a honking namespace.
from deploymachine import settings_deploymachine as settings


# The following core packages are essential for bootstrapping.
# Non-core packages to be installed via a configuration management recipe.
settings.BASE_OS_PACKAGES = [
    "build-essential",
    "git-core",
    "libjpeg62",
    "libjpeg62-dev",
    "libfreetype6",
    "libfreetype6-dev",
    "libzip-dev",
    "python-dev",
    "subversion",
    "libpq-dev",  # psycopg2
    "libxml2",  # django_compressor
    "libxml2-dev",  # django_compressor
    "libxslt1.1",  # django_compressor
    "libxslt1-dev",  # django_compressor
    #"gdal-bin",  # geodjango, not available on initial provision
]
if hasattr(settings, "EXTRA_BASE_OS_PACKAGES"):
    settings.BASE_OS_PACKAGES.append(settings.EXTRA_BASE_OS_PACKAGES)

# These Python packages are essential for bootstrapping.
settings.BASE_PYTHON_PACKAGES = [
    "Mercurial==2.0",
    "virtualenv==1.6.4",
    "Jinja2==2.6",
]
if hasattr(settings, "EXTRA_BASE_PYTHON_PACKAGES"):
    settings.BASE_PYTHON_PACKAGES.append(settings.EXTRA_BASE_PYTHON_PACKAGES)

if not hasattr(settings, "CONFIGURATORS"):
    settings.CONFIGURATORS = ["kokki"]  # Options "kokki", puppet", "chef"
