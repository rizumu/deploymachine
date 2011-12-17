Installation
============

Deploymachine runs locally on OSX or GNU/Linux.

Clone the deploymachine to an easily accesible folder on your local
machine. Replacing ``username`` with your local username, the
recommended place to clone is:

* ``/home/username/www/lib/deploymachine/`` for GNU/Linux
* ``/Users/username/www/lib/deploymachine/`` for OSX

Copy the example files and customize for your project. A suggestion is
to instead store these private files a private git repository, and
create symlinks to them. These files are set to be ignored in the
deploymachine's .gitignore::

    $ cp fabfile_local.dist.py fabfile_local.py
    $ cp deploymachine_settings.py.dist deploymachine_settings.py
    $ cp kokki-config.dist.j2 kokki-config.j2

You must also set some environment variables for your interactive
shell. For example, add the following to your ``~/.bashrc`` and edit
accordingly::
    export OPENSTACK_COMPUTE_USERNAME=""  # your rackspace username
    export OPENSTACK_COMPUTE_APIKEY=""  # your rackspace apikey
    export VIRTUALENVS_LOCAL_ROOT=""  # typically /home/username/.virtualenvs/
    export SITES_LOCAL_ROOT=""  # try /home/username/www/
