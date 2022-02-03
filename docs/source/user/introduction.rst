Introduction
============

``dj_blacksmith`` is available on PyPI, it can be installed
using pip.

.. code-block:: bash

   pip install dj_blacksmith


Or adding to a project using poetry by using

.. code-block:: bash

   poetry add dj_blacksmith


After wath, the library has to be configured as an installed app in the
django project.

.. code-block:: python

   INSTALLED_APPS = [
      ...,
      "dj_blacksmith"
      ...,
   ]


To finalize the client factory, the configuration is required and will be
documented in the next chapter.