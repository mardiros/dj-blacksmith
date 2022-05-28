Instanciating Client
====================

Now that the client has been configured, it can be used in views to
do http sub queries.

Follow the example below to instanciate the client.

Async
-----

In an async view, the blacksmith client

::

   from django.http import HttpRequest, HttpResponse
   from dj_blacksmith import AsyncDjBlacksmithClient

   async def hello_blacksmith(request: HttpRequest) -> HttpResponse:

      # Use a client
      dj_cli = AsyncDjBlacksmithClient(request)
      cli = await dj_cli("default")  # build the configured "default" client.
      api = await cli("api")  # resolve an endpoint to access to service "api".
      item = await api.foo.get({"id": 42})  # retrieve the item 42 from foo resources.

      return HttpResponse("Hello world", content_type="text/plain")

Sync
----

In an synchronous view, the blacksmith client

::

   from django.http import HttpRequest, HttpResponse
   from dj_blacksmith import SyncDjBlacksmithClient

   def hello_blacksmith(request: HttpRequest) -> HttpResponse:

      # Use a client
      dj_cli = SyncDjBlacksmithClient(request)
      cli = dj_cli("default")  # build the configured "default" client.
      api = cli("api")  # resolve an endpoint to access to service "api".
      item = api.foo.get({"id": 42})  # retrieve the item 42 from foo resources.

      return HttpResponse("Hello world", content_type="text/plain")
