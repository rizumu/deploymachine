Motivation
==========

Launching a high performance web application has community supported
best practices. DeployMachine attempts to put these best practices
into code, simplifying launching and growing the
application. DeployMachine follows the standards set forth by the
Slicehost provisioning documentation, the Django Deployment Workshop,
and the Arch Linux wiki.

* SLICEHOST PROVISIONING DOCS: http://articles.slicehost.com/ubuntu-10
* DJANGO DEPLOYMENT WORKSHOP: https://github.com/jacobian/django-deployment-workshop/
* ARCH LINUX WIKI: https://wiki.archlinux.org/

Each component and setting of the server stack really should be
understood inside out. However, sometimes it is prudent to install now
and learn later. DeployMachine attempts to help speed things along by
means of sensible defaults. Designed with server scalability in mind,
the idea is to start with one server and add or remove servers as
needed.

Media files and database backups are stored in Cloudfiles or S3 and the
application code and configuration is kept under version
control. Therefore all the DeployMachine's servers can be killed and
rebuilt in a matter of minutes, with no fear of data loss. Keep in
mind that killing the database server safely will require some
preparation and planning to ensure this.

Very little OS specific logic occurs in the DeployMachine, minus the
provision step. It is the job of Kokki, Puppet, or Chef to manage the
OS packages beyond bootstrapping.

Server Types
============

DeployMachine supports three server types:

* ``load balancer``
* ``application node``
* ``database server``

The current idea is to have one loadbalancer, one dbserver, and
potentially multiple appnodes. However, in the case of a small app, it
is probably best to start with a dbappblancer first. Or start with an
appbalancer and a dbserver as I have done. One the app demands, split
the loadbalncer off and scale each type individually.

.. note::

    **FUTURE FEATURE**

    A large app may need to add additional types of
    servers to the process such as a caching server, logging server,
    or a email server. A high traffic site will possibly need
    multiple database servers.

    Deploymachine is intent on supporting the most common and practical
    cases, but not the kitchen sink.
