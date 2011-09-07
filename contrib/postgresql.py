from fabric.api import local, user


def install_local_postgres(db_template="template_postgis", postgis_version="1.5"):
    """
    Show logs for a site.
    Usage:
        fab install_local_postgres:template_postgis,1.5

    First install postgres with gis bindings.
    OSX::
        brew install postgresql
        brew install postgis gdal
    """

    # Initialize database
    local("initdb -D /usr/local/pgsql/data")

    # Start postgres
    local("pg_ctl -D /usr/local/pgsql/data -l logfile start")

    # Create gis template, add PLPGSQL language support,
    # load the PostGIS SQL routines, enabling users to alter spatial tables.
    local("createdb -E UTF8 template_postgis -T template0", user="postgres")
    local("createlang -d template_postgis plpgsql", user="postgres")
    local("psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\"", user="postgres")

    # check postgis path for your distro
    local("psql -d template_postgis -f $(pg_config --sharedir)/contrib/postgis-1.5/postgis.sql", user="postgres")
    local("psql -d template_postgis -f $(pg_config --sharedir)/contrib/postgis-1.5/spatial_ref_sys.sql", user="postgres")
    local("psql -d template_postgis -c 'GRANT ALL ON geometry_columns TO PUBLIC;'", user="postgres")
    local("psql -d template_postgis -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'", user="postgres")
    local("createdb --template {0} --owner {1} {1}".format(db_template, name), user="postgres")

    # Create database user and database
    local("createuser --no-superuser --no-createdb --no-createrole {0}".format(name), user="postgres")
    local("psql --command \"ALTER USER {0} WITH PASSWORD '{1}';\"".format(name, password), user="postgres")
    local("createdb --template {0} --owner {1} {1}".format(db_template, name), user="postgres")
