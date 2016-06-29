===============
AppNexus-client
===============

General purpose Python client for the AppNexus API.

This library exists because most of the open-source solutions we found were
for specific AppNexus tasks, such as reporting. Our solution, however, is
meant to be used with any AppNexus service.

As it heavily relies on the AppNexus API, we advise you to read its
documentation_.

This client uses models in the same way that databases ORM does, but you can
also hook it to your own data representations class or simply use Python
dictionnaries.

.. _Documentation: https://wiki.appnexus.com/display/api/Home

Getting Started
===============

--------
services
--------

A service is an endpoint on the AppNexus API, representing an entity such as a
creative. Here is a complete list of services usable in this client:

 * AccountRecovery
 * AdProfile
 * Advertiser
 * AdQualityRule
 * AdServer
 * Brand
 * Broker
 * Browser
 * Campaign
 * Carrier
 * Category
 * City
 * ContentCategory
 * Country
 * Creative
 * CreativeFormat
 * Currency
 * CustomModel
 * CustomModelParser
 * Deal
 * DealBuyerAccess
 * DealFromPackage
 * DemographicArea
 * DeviceMake
 * DeviceModel
 * DomainAuditStatus
 * DomainList
 * ExternalInvCode
 * InsertionOrder
 * InventoryAttribute
 * InventoryResold
 * IpRangeService
 * Label
 * Language
 * LineItem
 * Lookup
 * NativeCustomKey
 * ManualOfferRanking
 * MediaSubtype
 * MediaType
 * Member
 * MobileApp
 * MobileAppInstance
 * MobileAppInstanceList
 * MobileAppStore
 * MemberProfile
 * ObjectLimit
 * OperatingSystem
 * OperatingSystemExtended
 * OperatingSystemFamily
 * OptimizationZone
 * Package
 * PackageBuyerAccess
 * PaymentRule
 * Pixel
 * Placement
 * PlateformMember
 * Profile
 * ProfileSummary
 * Publisher
 * Region
 * ReportStatus
 * Search
 * Segment
 * Site
 * TechnicalAttribute
 * Template
 * ThirdpartyPixel
 * User
 * UsergroupPattern
 * VisibilityProfile

------
Client
------

The AppNexus Client class is central to this package. It represents an access
to the AppNexus API. To initialize one, you just have to give it your
credentials :

.. code-block:: python

    from appnexus import AppNexusClient
    client = AppNexusClient("your-username", "super-secure-password")

You can then use it to retrieve or send data from and to the AppNexus API :

.. code-block:: python

    creative = client.creative.find_one(id=1337)
    creative["media_url"] = "http://test.com/"
    client.creative.modify(creative, id=1337)

------
Models
------

A model in appnexus-client is an abstraction for a service. Most of them are
already declared and you just have to import them.

Models needs an access to an AppNexus Client to work, you can give it to them
by either using the `connect` method or setting the client attribute to a
valid client. Thus, the two following lines are equivalent :

.. code-block:: python

    Profile.connect("your-username", "super-secure-password")
    Profile.client = AppNexusClient("your-username", "super-secure-password")

You can iterate through all the cities of AppNexus-API easily. For example,
to print the name of each and every city registered in AppNexus, you'd do :

.. code-block:: python

    for city in City.find():
        print(city["name"])

You can also retrieve a single result (The first one returned by the API)
using the find_one method :

.. code-block:: python

    city_i_care_about = City.find_one(id=1337)

---------------------
Filtering and sorting
---------------------

You can filter using parameters of the methods find and find_one. The
following loop prints all the registered French cities sorted by name :

.. code-block:: python

    for city in City.find(country_code="FR", sort="name.desc"):
        print(city["name"])

Explanations and documentation for filtering and sorting can be found on the
AppNexus-API's documentation, supplied at the beginning of this README.


--------------------------
Custom Data Representation
--------------------------

You can hook your own data representation class with this client. For this,
you must use a function that exposes this signature:

.. code-block:: python

    function(client, service, object)

The client is, of course, an AppNexusClient object. The service is a string
containing the service to which the object belongs. And finally, the object is
a python dictionnary containing data about an AppNexus entity. The return
value of this function will be used as a data representation.

To use this function and get the desired data representation, you must pass it
to the client through the `representation` keyword argument:

.. code-block:: python

    client = AppNexusClient("username", "password", representation=function)
