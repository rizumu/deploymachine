
External Libraries
==================

DeployMachine can be used with the following 3rd party libraries to
enhance the possibilities.


Openstack Compute
=================

DeployMachine supports the OpenStack Compute
API. `https://github.com/jacobian/openstack.compute
<https://github.com/jacobian/openstack.compute>`_

To view info on existing servers::

    $ openstack-compute list

.. note::

    **FUTURE FEATURE**

    Amazon EC2 and S3 support will be trivial to implement once desired.


Dnsimple
========

DeployMachine harnesses the dnsimple python API for directing our
domain names to our loadbalancer's ip, even after a
kill/create. @@@TODO


VirtualBox
==========

There is a fabfile method to boot virtualbox instances. This is useful
for testing in a developement environment. TODO: This hasn't been
tested in a while, consider harnessing Vagrant.
