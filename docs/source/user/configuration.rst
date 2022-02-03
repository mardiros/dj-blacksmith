Configuration
=============

When a django project is starting, it will configure blacksmith using
the settings module of the app, usually the ``DJANGO_SETTINGS_MODULE``
environment variable.


Loading resources
-----------------

The first setting is used to fillout the blacksmith registry.


.. code-block:: python

   BLACKSMITH_IMPORT = ["my.resources"]


Service Discovery
-----------------

A service discovery method has to be configured, and blacksmith discover
can be choosen following the example bellow.


Example using a static
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "sd": "static",
         "static_sd_config": {
            "srv": "http://srv:80",
            "api/v1": "http://api.v1:80",
         },
      },
   }

Example using a consul
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "sd": "consul",
         "consul_sd_config": {
            "addr": "http://consul:8500/v1",
            "service_name_fmt": "{service}-{version}",
            "service_url_fmt": "http://{address}:{port}/{version}",
            "unversioned_service_name_fmt": "{service}",
            "unversioned_service_url_fmt": "http://{address}:{port}",
         },
      },
   }


Example using the router
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "sd": "router",
         "router_sd_config": {
            "service_url_fmt":  "http://router/{service}-{version}/{version}",
            "unversioned_service_url_fmt": "http://router/{service}",
         },
      },
   }


Timeout
-------

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "timeout": {"read": 10, "connect": 5},
      },
   }


Proxies
-------

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "proxies": {
            "http://": "http://letmeout:8080/",
            "https://": "https://letmeout:8443/",
         },
      },
   }


Disable Certificate Verification
--------------------------------

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "verify_certificate": False,
      },
   }


.. important::

   | This let your application vulnerable to man-in-the-middle.
   | Great power came with great responsabilities.


::

   Updating the collection parser
   ------------------------------

   While consuming API that does not do bared collection, a collection parser
   has to be set in blacksmith to change the ``collection_get`` method that
   deserialize and build back the pyrantic model.

   .. code-block:: python

      BLACKSMITH_CLIENT = {
         "default": {
         },
      }


Middlewares
-----------

The blacksmith middlewares can also be configured using the configurator,
this is going to be documented in the next chapters.

In blacksmith, there are global middlewares per ``ClientFactory``, and
there are middlewares per ``Client``. Global :ref:`middlewares` are usefull for
metrics, tracing, caching, but they are not usesull for authentication in
a multi user application. :ref:`Middleware Factories` are usefull for that
purpose.
