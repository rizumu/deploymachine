from kokki import Directory, File, Template


Directory("{0}gunicorn/".format(env.config.deploy_home),
    mode=0755,
    owner="deploy",
    action="create")


for site in env.config.gunicorn.sites:
    File("{0}gunicorn/{1}.conf".format(env.config.deploy_home, site["name"]),
         content=Template("gunicorn/gunicorn.conf.j2",
             variables={
                 "name": site["name"],
                 "port": site["port"],
                 "worker_count": site["worker_count"],
                 "python_version": env.config.python_version,
                 "virtualenvs_root": env.config.virtualenvs_root,
             },
         ),
         owner="root",
         group="root",
         mode=0644)
