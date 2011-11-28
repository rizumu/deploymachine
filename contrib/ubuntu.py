from fabric.api import run

from deploymachine.conf import settings


def bootstrap_ubuntu(action="install"):
    # The following core packages are essential for bootstrapping.
    BASE_PACKAGES = [
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
        "gdal-bin",  # geodjango
    ]
    if hasattr(settings, "EXTRA_BASE_UBUNTU_PACKAGES"):
        BASE_PACKAGES.append(settings.EXTRA_BASE_UBUNTU_PACKAGES)

    # @@@ fix universe bug, where packages such as gdal-bin aren't found in apt-cache
    run("sed -i 's/universe/universe multiverse/g' /etc/apt/sources.list")
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("apt-get update && apt-get -y dist-upgrade")
    run("apt-get install -y {0}".format(" ".join(BASE_UBUNTU_PACKAGES)))
    bootstrap_salt()


def bootstrap_salt():
    raise NotImplementedError()
