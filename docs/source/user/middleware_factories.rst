.. _`Middleware Factories`:

Middleware Factories
====================

The middleware factory differ from the middleware in their need and usage.
A middleware is global, and, sometimes, middleware data may differ per
incoming requests.

The middleware factory, build a middleware and inject in in the blacksmith
client on instanciation.

The main use case is for forwardin header

Forward http headers
--------------------

The list of middleware are defined under the
setting keys ``middleware_factories`` and ``forwarded_headers``,
as in the example above.

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "sd": "router",
         "router_sd_config": {},
         "forwarded_headers": ["Authorization", "Accept-Language"],
         "middleware_factories": [
               "dj_blacksmith.AsyncForwardHeaderFactoryBuilder",
         ],
      },
   }


In this example, the ``forward_header`` middleware factory
will forward the ``Authorization`` header if present in the Django request,
to every blacksmith instanciated clients without writing a line of code.


Custom Middleware Factory
-------------------------

To load a custom middleware, a class can be passed on the same line

.. code-block:: python

   BLACKSMITH_CLIENT = {
      "default": {
         "sd": "router",
         "router_sd_config": {},
         "my_middleware_configuration": {"I can configure from this"},
         "middleware_factories": [
               "path.to.my.MyMiddlewareBuilder",
         ],
      },
   }


In the example above, the class ``MyMiddlewareBuilder`` overrides the class
:class:`pyramid_blacksmith.AbstractMiddlewareFactoryBuilder`.

The constructor of the class will received the whole ``default`` dict content,
and can configure itself throw the keys in it such as ``my_middleware_configuration``.