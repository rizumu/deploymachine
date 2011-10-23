from fabric.api import sudo


def ensite(site):
    "Enable an nginx site."
    sudo("/usr/sbin/nxensite {0}".format(site))
    reload_nginx()


def dissite(site):
    "Disable an nginx site."
    sudo("/usr/sbin/nxdissite {0} || true".format(site))
    reload_nginx()


def reload_nginx():
    "Gracefully restart an nginx site."
    sudo("/etc/init.d/nginx reload")
