.. _`Middlewares`:

Middlewares
===========

Blacksmith middleware can be configured using the settings ``BLACKSMITH_CLIENT``.

.. code-block::

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            # middlewares goes here.
         ],
      },
   }

.. note::

   When using the synchronous client, middleware prefixed with ``Sync`` must be used,
   otherwise, the ``Async`` version has to be configured.


Prometheus Middleware
---------------------

.. code-block::

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            "dj_blacksmith.SyncPrometheusMiddlewareBuilder",
            # Async users use the async version
            # "dj_blacksmith.AsyncPrometheusMiddlewareBuilder",
         ],
      },
   }

Circuit Breaker Middleware
--------------------------

.. code-block::

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            # middlewares goes here.
         ],
      },
   }

Collect Circuit Breaker in prometheus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Using redis as a storage backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _`HTTP Cache Middleware`:

HTTP Cache Middleware
---------------------

.. code-block::

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            # middlewares goes here.
         ],
      },
   }
