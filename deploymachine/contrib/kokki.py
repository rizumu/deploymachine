import json

from fabric.api import cd, env, local, sudo, put
from fabric.contrib.files import upload_template
from fabric.decorators import task

import deploymachine_settings as settings


@task
def kokki():
    """
    Cook all nodes which identically match the given role's ``env.server_types``. Servers
    are defined in ``settings.OPENSTACK_SERVERS`` and configruation in ``kokki-config.j2``

    Ex. Cook the ``settings.OPENSTACK_SERVERS`` which contain only the ``["appnode"]`` role:
        fab appnode kokki

    Ex. Cook the ``settings.OPENSTACK_SERVERS`` which identically match the
    ``["loadbalancer", "appnode", "dbserver", "cachenode"]`` roles:
        fab allinone kokki

    """
    public_ip_addresses = openstack_get_ips(env.server_types, port=settings.SSH_PORT, append_port=False)
    upload_template("kokki-config.j2", "/home/deploy/kokki-config.py",
                     context={"deploymachine_settings": settings}, use_jinja=True)
    for public_ip in public_ip_addresses:
        # put the local cookbooks on the server
        local("rsync -e 'ssh -p {0}' -avzp {1}kokki-cookbooks/ {2}@{3}:/home/deploy/kokki-cookbooks/".format(
               settings.SSH_PORT, settings.DEPLOYMACHINE_LOCAL_ROOT, settings.DEPLOY_USERNAME, public_ip))
    for role in env.server_types:
        # run kokki
        with cd(settings.DEPLOY_HOME):
            sudo("kokki -f kokki-config.py {0} -o fabric_env='{1}'".format(role, json.dumps(env)))

