import os

from fabric.api import cd, env, local, sudo
from fabric.api import settings as fab_settings

from deploymachine.conf import settings

from deploymachine.contrib.openstack_api import openstack_get_ips


def pg_install_local(dbtemplate="template_postgis", postgis_version="1.5"):
    """
    Show logs for a site.

    tip: make sure your local user is also a postgres superuser

        sudo su postgres
        createuser username

    Usage:
        fab install_local_postgres:template_postgis,1.5

    First install postgres with gis bindings.
    OSX::
        sudo pip install numpy
        brew install postgresql
        brew install postgis gdal

    If you get the error: "FATAL: role is not permitted to log in",
    try manually granting the privilege to login on your database user
    account. This can be done by executing the following as postgres
    in the psql prompt::

        ALTER ROLE <username> LOGIN;

    To upgrade an existing pg install, do something like this:

        sudo -u postgres pg_upgrade -d /var/lib/postgres-old/data -D /var/lib/postgres/data -b /tmp/usr/bin/ -B /usr/bin
    """
    raise NotImplementedError()  # this is just documentation for now
    local("sudo su postgres && createuser yourusername")

    # Initialize database
    local("initdb -D /usr/local/pgsql/data")

    # Start postgres
    local("pg_ctl -D /usr/local/pgsql/data -l logfile start")

    # Create gis template, add PLPGSQL language support,
    # load the PostGIS SQL routines, enabling users to alter spatial tables.
    local("createdb -E UTF8 template_postgis -T template0")
    local("createlang -d template_postgis plpgsql")
    local("psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\" -U postgres")

    # check postgis path for your distro
    local("psql -d template_postgis -f $(pg_config --sharedir)/contrib/postgis-1.5/postgis.sql -U postgres")
    local("psql -d template_postgis -f $(pg_config --sharedir)/contrib/postgis-1.5/spatial_ref_sys.sql -U postgres")
    local("psql -d template_postgis -c 'GRANT ALL ON geometry_columns TO PUBLIC;' -U postgres")
    local("psql -d template_postgis -c 'GRANT ALL ON geography_columns TO PUBLIC;' -U postgres")
    local("psql -d template_postgis -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;' -U postgres")

    # Create database user and database
    local("createuser --no-superuser --no-createdb --no-createrole {0}".format(dbname))
    local("psql -d template_postgis --command \"ALTER USER {0} WITH PASSWORD '{1}';\"".format(dbname, password))
    local("createdb  -E UTF8 --template {0} --owner {1} {1}".format(dbtemplate, dbname))


def pg_dblaunch(dbname, password, dbtemplate="template_postgis"):
    """
    Launches a new database. Typically used when launching a new site.
    The default database template is ``template_postgis`` for GeoDjango.
    An standard when not using GeoDjango is ``template1``.
    """
    sudo("createuser --no-superuser --no-createdb --no-createrole {0}".format(dbname), user="postgres")
    sudo("psql --command \"ALTER USER {0} WITH PASSWORD '{1}';\"".format(dbname, password), user="postgres")
    sudo("createdb -E UTF8 --template {0} --owner {1} {1}".format(dbtemplate, dbname), user="postgres")


def pg_dbrestore_local(dbname, path_to_dump_file, dbtemplate="template_postgis"):
    """
    Usage:
        fab pg_dbrestore_local:scenemachine,/home/deploy/dbdumps/scenemachine.dump

    tip: make sure your local user is also a postgres superuser
    tip: setup a local cronjob to sync backups
         0 0 0 0 * postgres duplicity cf+http://dbdumps /home/rizumu/dbdumps
    """
    if not dbtemplate == "template_postgis":
        raise NotImplementedError()
    with fab_settings(warn_only=True):
        local("dropdb {0}".format(dbname))
        local("createdb --template={0} --owner={1} {1}".format(dbtemplate, dbname))
        local("pg_restore --dbname={0} {1}".format(dbname, path_to_dump_file))


def pg_dbrestore(dbname, dbtemplate="template_postgis", keep_tmp=True):
    """
    Usage:
        fab dbserver pg_dbrestore:scenemachine

    tip: make sure your local user is also a postgres superuser
    """
    dump_filename = "{0}-fabric-auto.dump".format(dbname)
    remote_dump_file = os.path.join(settings.DBDUMPS_ROOT, dump_filename)
    sudo("pg_dump -Fc {0} > {1}".format(dbname, remote_dump_file), user="postgres")
    local("scp -P {0} {1}@{2}:{3} /tmp/{4}".format(
        settings.SSH_PORT,
        settings.DEPLOY_USERNAME,
        openstack_get_ips(env.server_types, append_port=False)[0],
        os.path.join(settings.DBDUMPS_ROOT, dump_filename),
        dump_filename))
    pg_dbrestore_local(dbname, "/tmp/{0}".format(dump_filename), dbtemplate="template_postgis")
    sudo("rm {0}".format(remote_dump_file))
    if keep_tmp:
        local("rm /tmp/{0}".format(dump_filename))


def pg_dbrestore_prod(dbname, dump_filename, dbtemplate="template_postgis"):
    if not dbtemplate == "template_postgis":
        raise NotImplementedError()
    with fab_settings(warn_only=True):
        with cd(settings.DBDUMPS_ROOT):
            sudo("dropdb {0}".format(dbname), user="postgres")
            sudo("createdb -E UTF8 --template={0} --owner={1} {1}".format(dbtemplate, dbname), user="postgres")
            sudo("pg_restore --dbname={0} {1}{2}".format(dbname, settings.DBDUMPS_ROOT, dump_filename), user="postgres")
