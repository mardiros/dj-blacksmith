Introduction
============

``dj_blacksmith`` is available on PyPI, it can be installed
using pip.

.. code-block:: bash

   pip install dj_blacksmith


Or adding to a project using poetry by using

.. code-block:: bash

   poetry add dj_blacksmith


After wath, the library has to be configured throw the pyramid
configurator using the command

.. code-block:: python

   with Configurator(settings=settings) as config:
      config.include('dj_blacksmith')


in the code or using the `.ini` file configuration


.. code-block:: ini

   pyramid.includes =
      dj_blacksmith



To finalize the client factory, the configuration is required and will be
documented in the next chapter.