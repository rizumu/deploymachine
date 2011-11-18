First Deployment
================
After private/personal configuration is complete, the general idea is
as follows. From bare metal to production ready::

    $ fab openstack_bootem
    $ fab root provision
    $ fab dbserver launch
    $ fab loadbalancer launch
    $ fab appnode launch

The ``fab openstack_bootem`` command runs the ``openstack_boot`` command for each server
defined in the ``settings.py``. To list the details for your new
machines, including ip addresses::

    $ openstack-compute list

The ``fab root provision`` command tries to provision each server
defined in the settings, skipping those which have already been
provisioned. Provisioning configures core ubuntu packages, ssh,
firewall, python, kokki, and root accounts. Security follows the best
practice guidelines of the excellent Slicehost documentation. After
provisioning is complete you can manually login to the machine using
the following format::

    $ ssh -p {port} deploy@{ip}

The ``fab apptype launch`` is called once for each server type and
it's goal is to take the newly provisioned servers to a production
ready state. The launch command tells Kokki to cook the server to the
custom specification defined in defined in the
``kokki-config.yaml``. See ``kokki-config.yaml.dist`` for an example.

.. warning::

    Currently untested with all possible combinations and quantities
    of server types.


Scaling up and down
===================
First start with a combined dbappbalancer, then when necessary split
into an appbalancer and dbserver, followed by loadbalancer, appnode,
dbserver.

Once appli cation growth warrants more power, increase/decrease the
number of appnodes, add a cachenode, lognode, or tasknode.

Growth beyond this can only suggest that the application is bringing
in revenue. The good news is that the deploymachine has already
prepared the application for further expansion by neatly separating
repsonsibility between services.

.. warning::

    * Currently implemented are loadbalancer, appnode, dbserver and
      appbalancer.
    * Not yet implemented are dbappbalacner, cachenode, lognode or
      tasknode.
    * The splitting process is not yet implemented, stay tuned.


Ongoing Deployments
===================
To add a new app node to the mix follow this three step process::

    $ fab openstack_boot appnode2
    $ fab root provision
    $ fab appnode launch
    $ fab kokki:loadbalancer

Deploy machine provides a Fabric API for maintaining your
application. Commands for git, pip, supervisor, nginx, django and more
are included. Take a peek inside the ``contrib`` folder for all the
available options, or help extend the existing library. Domain
specific commands can be imported from your personal in
``fab_local.py``. An example ``fab_local.example.py`` is included.
