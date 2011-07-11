Installation
============

DeployMachine runs locally on OSX or GNU/Linux. It builds the current
version of Ubuntu Server. @@@ Debian, Fedora and Arch support are next
in the queue.

Clone the deploymachine to an easily accesible folder on your local
machine. Replacing ``username`` with your local username, the
recommended place to clone is:

* ``/home/username/www/lib/deploymachine/`` for GNU/Linux
* ``/Users/username/www/lib/deploymachine/`` for OSX

Copy the example files and customize for your project. A suggestion is
to instead store these private files a private git repository, and
create symlinks to them. These files are set to be ignored in the
deploymachine's .gitignore::

    $ cp fabfile_local.example.py fabfile_local.py
    $ cp settings_deploymachine.example.py settings_deploymachine.py
    $ cp kokki-config.example.j2 kokki-config.j2

Copy or symlink the public keys to be authorized access to all servers
in the ``ssh folder`` of the deploymachine project. These files are
set to be ignored in the deploymachien's .gitignore::

    $ cp ~/.ssh/me.pub ~/www/lib/deploymachine/ssh/me.pub
    $ cp ~/.ssh/you.pub ~/www/lib/deploymachine/ssh/you.pub
    $ cp ~/.ssh/her.pub ~/www/lib/deploymachine/ssh/her.pub

Install the requirements into your local site-packages of the python
environment. The suggestion is to use virtualenv to create a
virtualenv named ``deploymachine``::

    $ virtualenv --no-site-packages --distribute deploymachine
    $ pip install -r requirements.txt

See http://pypi.python.org/pypi/virtualenv and
http://pypi.python.org/pypi/pip if you are unfamiliar with either pip
or virtualenv and learn how to use them before going any further.
