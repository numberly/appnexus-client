############
Get Started!
############

AppNexus-client is really simple to use. I will show you how to leverage it to
do some simple operations like changing the names of your campaigns, adding a
new city to a geotargeting or upload a creative.

============
AppNexus API
============

AppNexus-client extensively use the AppNexus-API, which allow its users to make
changes to AppNexus entities with scripts or applications.

We advise you to keep the `API documentation`_ near you, since you will find all
business logic in it. AppNexus-client is only an intermediate between you and
the API.

==========
connection
==========

First, you need to connect to the AppNexus API.

.. code-block:: python

    from appnexus import connect
    connect("my-username", "my-password")

And that's it. You now have access to a `appnexus.client` object which holds
connection informations for you and that you can use to access the API.

========
Services
========

The services_ are URLs used by appnexus as an interface for a specific type of
data. For example, you have a service for campaigns, another one for creatives,
another one for profiles (contain targeting informations), and the list goes
on.

Through your uses of the AppNexus-client, you will often need to precise on
which service you want an operation to be done. For example, if you need to
interact with `Domain Lists`_

.. _`API documentation`: https://wiki.appnexus.com/display/api/Home
.. _services: https://wiki.appnexus.com/display/api/API+Services
.. _`Domain Lists`: https://wiki.appnexus.com/display/api/Domain+List+Service
