.. image:: https://img.shields.io/pypi/v/appnexus-client.svg?maxAge=3600

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

------
Models
------

A model in appnexus-client is an abstraction for a service. Most of them are
already declared and you just have to import them.

You can access the fields of an AppNexus entity the same way you'd do to access
a dict's values : `entity["field_name"]`

You can also iterate through all the cities of AppNexus-API easily. For
example, to print the name of each and every city registered in AppNexus, you'd
do :

.. code-block:: python

    from appnexus import City
    for city in City.find():
        print(city["name"])

You can also retrieve a single result (The first one returned by the API)
using the find_one method :

.. code-block:: python

    city_i_care_about = City.find_one(id=1337)

---------------------
Filtering and sorting
---------------------

Sorting with appnexus-client is easy. Just give a `sort` parameter with a value
indicating which field is sorted in which order (`asc` or `desc`). This
parameter will be supplied to the AppNexus API which will return a sorted
response.

You can filter entities using parameters of the methods find and find_one. Each
parameter stand as a new filter for the field it is named after. For example,
you can search for cities whose `country_code` field is equal to "FR" and sort
them by name:

.. code-block:: python

    for city in City.find(country_code="FR", sort="name.desc"):
        print(city["name"])

The parameters you give to the `find` and `find_one` methods are translated
into query parameters for the requests being send. For example, the snippet
`Creative.find(state="active", advertiser_id=[1, 2, 3])` will result in a get
request on `http://api.appnexus.com/creative?state=active&advertiser_id=1,2,3`

Please search in the documentation_ to understand the meaning of each
parameter.

--------------------------
Custom Data Representation
--------------------------

You can hook your own data representation class with appnexus-client. For this,
you must use a function that exposes this signature:

.. code-block:: python

    function(client, service, object)

The client is, of course, an AppNexusClient instance. The service must be a
string representing the service to which the object belongs. And finally, the
object is a python dictionnary containing data about an AppNexus entity. The
return value of this function will be used as a data representation.

To use this function and get the desired data representation, you must pass it
to the client through the `representation` keyword argument.

If you want to retrieve data as a list of tuples instead of a dict, you could
do the following:

.. code-block:: python

    def tuple_representation(client, service, object):
        return object.items()
    connect("username", "password", representation=tuple_representation)
