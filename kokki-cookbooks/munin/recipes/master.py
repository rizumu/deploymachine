import openstack.compute

from kokki import Package, Directory, File, Template


Package("munin")


def get_munin_nodes():
    node_list = []
    compute = openstack.compute.Compute(username=env.config.openstack_compute.username,
                                        apikey=env.config.openstack_compute.api_key)
    for server in compute.servers.list():
        if "loadbalancer" in server.name:
            node_list.append(dict(name=server.name, ip="127.0.0.1"))
        else:
            node_list.append(dict(name=server.name, ip=server.addresses["private"][0]))
    return node_list


Directory(env.config.munin.dbdir,
    owner="munin",
    group="munin",
    mode=0755)


File("/etc/munin/munin.conf",
    owner="root",
    group="root",
    mode=0644,
    content=Template(
        "munin/munin.conf.j2",
         variables=dict(
             munin_hosts=get_munin_nodes()
    )))
