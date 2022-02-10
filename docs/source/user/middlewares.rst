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
         # Optional settings with default values
         # "metrics": {
         #    "buckets": [0.05 * 2 ** x for x in range(10)],
         #    "hit_cache_buckets": [0.005 * 2 ** x for x in range(10)],
         # },
      },
   }

The ``buckets`` setting is used to configure the histogram of http requests,
and the ``hit_cache_buckets`` is used to configure the histogram for the http
requests response comming from the :ref:`HTTP Cache Middleware`.


Circuit Breaker Middleware
--------------------------

.. code-block::

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            "dj_blacksmith.SyncCircuitBreakerMiddlewareBuilder",
            # Async users use the async version
            # "dj_blacksmith.AsyncCircuitBreakerMiddlewareBuilder",
         ],
         # Optional settings with default values
         # "circuit_breaker": {
         #    "threshold": 5,
         #    "ttl": 30,
         # }
      },
   }

Collect Circuit Breaker in prometheus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To properly works together, middleware must be added in this order:

.. code-block:: ini

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            "dj_blacksmith.SyncPrometheusMiddlewareBuilder",
            "dj_blacksmith.SyncCircuitBreakerMiddlewareBuilder",
            # Async users use the async version
            # "dj_blacksmith.AsyncPrometheusMiddlewareBuilder",
            # "dj_blacksmith.AsyncCircuitBreakerMiddlewareBuilder",
         ],
      },
   }


.. Using redis as a storage backend
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. _`HTTP Cache Middleware`:

HTTP Cache Middleware
---------------------

.. code-block::

   BLACKSMITH_CLIENT = {
      "default": {
         ...,
         "middlewares": [
            # middlewares goes here.
            "dj_blacksmith.SyncHTTPCacheMiddlewareBuilder",
            # Async users use the async version
            # "dj_blacksmith.AsyncHTTPCacheMiddlewareBuilder",
         ],
         "http_cache": {
            "redis": "redis://host.example.net/42",
            # Optional settings with default values
            # "policy": "blacksmith.CacheControlPolicy",
            # "serializer": "blacksmith.JsonSerializer",
         }
      },
   }
