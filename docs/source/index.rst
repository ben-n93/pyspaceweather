pyspaceweather
==============

`pyspaceweather` is a Python wrapper for the Australian Bureau of Metererology's `Space Weather API <https://sws-data.sws.bom.gov.au/>`_.

The API provides access to near real-time data from the BOM's Australian Space Weather Forecasting Centre.

With this wrapper you can more easily and quickly get data from the web API.

Installation
------------

You can use pip to install: 

.. code-block:: bash

    pip install pyspaceweather

.. _quickstart:

Alternatively, you can grab the latest source code from GitHub:

.. code-block:: bash

   git clone https://github.com/ben-n93/pyspaceweather.git
   cd pyspaceweather
   pip install .

Quickstart
----------

An API key, which you can get from the BOM, is required to use the API:

.. code-block:: python

   import os

   from pyspaceweather import SpaceWeather

   sw = SpaceWeather(os.environ["SPACEWEATHER_API_KEY"])

Each API request method is available as a method of ``SpaceWeather``.

For example, to get details of any magnetic alert current for the Australian region:

.. code-block:: python

   alert_warnings = sw.get_mag_alert()

What's returned is a list of ``MagAlert`` objects (or an empty list, if there is no data availiable):

.. code-block:: python

   [MagAlert(start_time=datetime.datetime(2015, 2, 7, 8, 45),
   valid_until=datetime.datetime(2015, 2, 7, 20, 45),
   g_scale=1,
   description='minor')
   ]

Or, to get historical A-index values, you can call ``get_a_index()``, passing a string or datetime object to the relevant parameters:

.. code-block:: python

   a_index_data = sw.get_a_index(start="2023-01-01 00:00:00", end=datetime(2023, 12, 1, 12, 30))


License
-------
`pyspaceweather` is made available under the MIT License. For more details, see LICENSE.md.


API Reference
-------------
.. toctree::
   :maxdepth: 2

   reference

