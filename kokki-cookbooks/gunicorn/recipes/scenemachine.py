
from kokki import Package, Directory, File, Template, Service


#@@@ Hardcoded paths, retrieve from deploymachine variables
Directory("/home/deploy/gunicorn/",
    mode = 0755,
    owner = "deploy",
    action = "create")


for site in env.config.gunicorn.sites:
    File("/home/deploy/gunicorn/{0}.conf".format(site["name"]),
         content=Template("templates/gunicorn.conf.j2",
             variables={
                 "name": site["name"],
                 "port": site["port"],
                 "worker_count": site["worker_count"],
                 "python_version": "2.6", # TODO: Version shouldn't be hardcoded
             }
         ),
         owner = "root",
         group = "root",
         mode = 0644)
