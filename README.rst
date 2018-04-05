.. _documentation: https://wiki.appnexus.com/display/api/Home
.. _Thingy: https://github.com/numberly/thingy

===============
AppNexus-client
===============

.. image:: https://img.shields.io/pypi/v/appnexus-client.svg
   :target: https://pypi.python.org/pypi/appnexus-client
.. image:: https://img.shields.io/github/license/numberly/appnexus-client.svg
   :target: https://github.com/numberly/appnexus-client/blob/master/LICENSE
.. image:: https://img.shields.io/travis/numberly/appnexus-client.svg
   :target: https://travis-ci.org/numberly/appnexus-client
.. image:: https://img.shields.io/coveralls/numberly/appnexus-client.svg
   :target: https://coveralls.io/github/numberly/appnexus-client
.. image:: http://readthedocs.org/projects/appnexus-client/badge
   :target: http://appnexus-client.readthedocs.io

|

General purpose Python client for the AppNexus API.

This library exists because most of the open-source solutions we found were for
specific AppNexus tasks, such as reporting. Our solution, however, is meant to
be used with any AppNexus service.

As it heavily relies on the AppNexus API, we advise you to read its
documentation_.

This client uses models in the same way that database ORM would do, but you can
also hook it to your own data representation class, or simply use Python
dictionaries.


Install
=======

.. code-block:: sh

    $ pip install appnexus-client


Getting started
===============

Services
--------

A service is an endpoint on the AppNexus API, representing an entity such as a
creative. Here is the complete list of services usable with AppNexus-client:
``AccountRecovery``, ``AdProfile``, ``AdQualityRule``, ``AdServer``,
``Advertiser``, ``Brand``, ``Broker``, ``Browser``, ``Campaign``, ``Carrier``,
``Category``, ``City``, ``ContentCategory``, ``Country``, ``Creative``,
``CreativeFormat``, ``Currency``, ``CustomModel``, ``CustomModelParser``,
``Deal``, ``DealBuyerAccess``, ``DealFromPackage``, ``DemographicArea``,
``DeviceMake``, ``DeviceModel``, ``DomainAuditStatus``, ``DomainList``,
``ExternalInvCode``, ``InsertionOrder``, ``InventoryAttribute``,
``InventoryResold``, ``IpRangeList``, ``Label``, ``Language``, ``LineItem``,
``Lookup``, ``ManualOfferRanking``, ``MediaSubtype``, ``MediaType``, ``Member``,
``MemberProfile``, ``MobileApp``, ``MobileAppInstance``,
``MobileAppInstanceList``, ``MobileAppStore``, ``NativeCustomKey``,
``ObjectLimit``, ``OperatingSystem``, ``OperatingSystemExtended``,
``OperatingSystemFamily``, ``OptimizationZone``, ``Package``,
``PackageBuyerAccess``, ``PaymentRule``, ``Pixel``, ``Placement``,
``PlatformMember``, ``Profile``, ``ProfileSummary``, ``Publisher``, ``Region``,
``ReportStatus``, ``Search``, ``Segment``, ``Site``, ``TechnicalAttribute``,
``Template``, ``ThirdpartyPixel``, ``User``, ``UsergroupPattern``, ``VisibilityProfile``,
and ``Report``


Connecting
----------

First of all, you need to connect the client to AppNexus. One simple way is to
use the ``connect`` function with your credentials:

.. code-block:: python

    from appnexus import connect

    connect("my-username", "my-password")

From there, you can use all the features of the library.


Models
------

A model in AppNexus-client is an abstraction for a service. Most of them are
already declared and you just have to import them.

You can access the fields of an AppNexus just like any object:
``entity.field_name``

For example, to print the name of each and every city registered in AppNexus,
you could do:

.. code-block:: python

    from appnexus import City

    for city in City.find():
        print(city.name)

You can also retrieve a single result (the first one returned by the API) using
the ``find_one`` method:

.. code-block:: python

    city = City.find_one(id=1337)


Filtering and sorting
---------------------

Sorting with AppNexus-client is easy: just give a ``sort`` parameter with a
value indicating which field is sorted in which order (``asc`` or
``desc``). This parameter will be supplied to the AppNexus API which will
return a sorted response.

You can filter entities using parameters of the methods ``find`` and
``find_one``. Each parameter stand as a new filter for the field it is named
after. For example, you can search for cities whose `country_code` field is
equal to "FR" and sort them by name:

.. code-block:: python

    for city in City.find(country_code="FR", sort="name.desc"):
        print(city.name)

The parameters you give to the ``find`` and ``find_one`` methods are translated
into query parameters for the requests being send. For example, the snippet
``Creative.find(state="active", advertiser_id=[1, 2, 3])`` will result in a get
request on ``http://api.appnexus.com/creative?state=active&advertiser_id=1,2,3``

Please search in the AppNexus API documentation_ to understand the meaning of
each parameter.


Custom data representation
--------------------------

By default, AppNexus-client relies on Thingy_ to represent data as objects.

But you can also hook your own data representation class. For this, you must
use a function that exposes this signature:

.. code-block:: python

    function(client, service, object)

The ``client`` argument is an ``AppNexusClient`` instance. ``service`` must be a
string representing the service to which the object belongs. ``object`` is a
python dictionary containing data about an AppNexus entity. The return value of
this function will be used as the data representation.

To use this function and get the desired data representation, you must pass it
to the client as the ``representation`` keyword argument.

For example, if you would want your data to be in the form of simple
dictionaries you would do the following:

.. code-block:: python

    def dict_representation(client, service, object):
        return object.view()

    connect("username", "password", representation=dict_representation)


Reports
-------

Retrieving report data has 3 steps:

1. Creating a report
2. Check if the report is ready to download
3. Download the report

.. code-block:: python

    from appnexus import Report

    json = {
        "report_type": "network_analytics",
        "columns": [
            "clicks",
            "total_convs",
            "insertion_order_id",
            "line_item_id",
        ],
        "report_interval": "lifetime",
        "format": "csv"
    }

    report = Report(json).save()
    data = report.download()


The ``download`` method on ``Report`` object takes care of checking if the report is
available for download and retires it by default for 3 times with an interval of 1 second.
The number of retries can be overridden by passing the parameter ``retry_count`` to the ``download``
method

.. code-block:: python

    # Increase retry count
    data = report.download(retry_count=5)


Tests
=====

To run AppNexus-client tests:

* install developers requirements with ``pip install -r requirements.txt``;
* run ``pytest``.


License
=======

MIT
