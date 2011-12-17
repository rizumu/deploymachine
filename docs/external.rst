
External Libraries
==================

Deploymachine can be used with the following 3rd party libraries to
enhance the possibilities.


CLoud Providers
===============

Deploymachine supports both the Rackspace Openstack API and the Amazon
Boto API via the bootmachine project.

Dnsimple
========

Deploymachine harnesses the dnsimple python API for directing our
domain names to our loadbalancer's ip, even after a
kill/create. @@@TODO

NewRelic
========
For Python application monitoring.

VirtualBox
==========

There is a fabfile method to boot virtualbox instances. This is useful
for testing in a developement environment.

.. todo::
    This hasn't been tested in a while and we should be
    considering harnessing Vagrant.
