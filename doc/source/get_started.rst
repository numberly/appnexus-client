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
Connection
==========

First, you need to connect to the AppNexus API with an ``AppNexusClient``
object.  A shortcut is to use the connect method:

.. code-block:: python

    from appnexus import connect
    connect("my-username", "my-password")

And that's it. You now have access to ``appnexus.client`` which holds
connection informations for you and that you can use to access the API.

========
Services
========

The services_ are URLs used by appnexus as an interface for a specific type of
data. For example, you have a service for campaigns_, another one for
creatives_, another one for profiles_ (contain targeting informations), and the
list goes on.

Through your uses of the AppNexus-client, you will often need to precise on
which service you want an operation to be done. For example, if you need to
interact with `Domain Lists`_, you will need to precise the endpoint to be
"domain-list". Service are normalized by lowering theme and using hyphens
instead of spaces.

Within python, you can access these services with any ``AppNexusClient`` instance, using it's name. it would be ``client.campaign`` to get the "campaign" service. 

===============
Retrieval by id
===============

You can use the ``find_one`` method on any service.

.. _`API documentation`: https://wiki.appnexus.com/display/api/Home
.. _services: https://wiki.appnexus.com/display/api/API+Services
.. _campaigns: https://wiki.appnexus.com/display/api/Campaign+Service
.. _creatives: https://wiki.appnexus.com/display/api/Creative+Service
.. _profiles: https://wiki.appnexus.com/display/api/Profile+Service
.. _`Domain Lists`: https://wiki.appnexus.com/display/api/Domain+List+Service
