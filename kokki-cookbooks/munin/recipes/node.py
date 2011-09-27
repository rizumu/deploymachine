import openstack.compute

from kokki import Package, File, Template, Service, Fail


Package("munin-node")


def get_munin_master_ip():
    compute = openstack.compute.Compute(username=env.config.openstack_compute.username,
                                        apikey=env.config.openstack_compute.api_key)
    for server in compute.servers.list():
        if "balancer" in server.name:  # matches loadbalancer, appbalancer, dbappbalancer
            return server.addresses["private"][0]
    raise Fail("Could not find the munin-master aka loadbalancer.")


File("munin-node.conf",
    path="/etc/munin/munin-node.conf",
    owner="root",
    group="root",
    mode=0644,
    content=Template(
        "munin/munin-node.conf.j2",
        variables=dict(
            munin_master_ip=get_munin_master_ip()
    )))


Service("munin-node",
    subscribes=[("restart", env.resources["File"]["munin-node.conf"])])


File("/etc/munin/plugin-conf.d/python",
    owner="root",
    group="root",
    mode=0644,
    content=(
        "[*]\n"
        "env.PYTHON_EGG_CACHE /tmp/munin-egg-cache\n"
    ),
    notifies=[("restart", env.resources["Service"]["munin-node"])])


if env.system.ec2:
    File("/etc/munin/plugins/if_err_eth0",
        action="delete",
        notifies=[("restart", env.resources["Service"]["munin-node"])])
