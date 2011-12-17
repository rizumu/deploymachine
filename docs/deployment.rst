First Deployment
================
After private/personal configuration is complete, the general idea is
as follows::

    $ fab dbserver launch
    $ fab loadbalancer launch
    $ fab appnode launch

.. warning::

    Currently untested with all possible combinations and quantities
    of server types.


Scaling up and down
===================
First start with a combined dbappbalancer, then when necessary split
into an appbalancer and dbserver, followed by loadbalancer, appnode,
dbserver.

Once application growth warrants more power, increase/decrease the
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
First use the bootmachine to launch and provision your new machine::

    $ fab openstack.boot appnode2
    $ fab root provision

Next to add a new app node to the mix follow this process::

    $ fab appnode launch
    $ fab kokki:loadbalancer

Deploymachine provides a Fabric API for maintaining your
application. Commands for git, pip, supervisor, nginx, django and more
are included or type ``fab -l``. Take a peek inside the ``contrib``
folder for all the available options, or help extend the existing
library. Domain specific commands can be imported from your personal
in ``fab_local.py``. An example ``fab_local.example.py`` is included.
