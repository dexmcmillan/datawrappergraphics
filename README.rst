========================
DATAWRAPPER GRAPHICS
========================

An (unofficial!) package for Datawrapper that allows you to interface between your pandas dataframes and Datawrapper locator maps, charts, and folders in Python.

======================
INSTALLATION AND SETUP
======================
Install using pip:

``pip install datawrappergraphics``

Datawrappergraphics uses Datawrapper's API to interface with Datawrapper. In order to use it, you need to generate an API token with the following permissions:

- Auth: read/write
- Chart: read/write
- Folder: read/write

This token can be generated in *settings > API-Tokens*. There are three ways to authenticate:

1. By default, Datawrappergraphics will look for an environment variable called ``DW_AUTH_TOKEN``.
2. You can upload a ``auth.txt`` file in your project's root directory containing only your authentication key (don't forget to add this file to your .gitignore!).
3. You can pass your token on instantiation using the ``auth_token`` arg.

Once you've authenticated, you're good to go!

====================
USAGE
====================
There are currently two main classes that can be implemented using this module:

* Map - This is a datawrapper locator map.
* Chart - This is a datawrapper chart.

Each of these classes inherits from the DatawrapperGraphic class, which is not meant to be implemented directly.

Classes can be implemented by using:

.. code-block:: python

        import datawrappergraphics

        chart_id = "AbBe1"

        map = (Map()
                .data(aPandasDataframe)
                .head("A cool headline for your chart")
                .deck("A great looking deck, or subheadline, for your chart".)
                .footer("This is a note")
        )

==========================
GUIDE
==========================

Some simple usage patterns. Get started by importing the package:

.. code-block:: python

        import datawrappergraphics as dwg

Create a new chart.
==========================

.. code-block:: python

        dwg.Chart()

Copy an existing chart.
==========================

This will create a brand new chart by copying another chart. Useful if you've made a "template chart" and want to create a bunch of charts using different data based on that template.

.. code-block:: python

        dwg.Chart(copy_id="AbCd1")


Upload data to an existing chart.
==========================

Data is uploaded as a pandas dataframe. Charts do not require any special columns, so go wild with it.

.. code-block:: python

        dwg.Chart(chart_id="AbCd1").data(df)


Upload data to an existing locator map
==========================

The Map class is used to interact with locator map data. Your dataframe has to have a few required columns:

- **Type**: Either "point" or "area", depending on whether the row is a point marker or an area.
- **latitude/longitude** or **geometry**: Point markers use two columns to locate: latitude and longitude. Area markers need a geometry column with WKT in the rows.

When you're uploading your data, you can specify a number of optional columns to control how your marker points show:

- Point markers:
    - **icon**: Specify the id of any icon available in Datawrapper's locator maps. Default: circle.
    - **markerColor**: What color the marker shows up as. Default: #C42127.
  
- Area markers:
    - **fill**: A 6-digit hexcode or a boolean value that controls the fill color or visibility of the marker fill. Default: #C42127.
    - **stroke**: A 6-digit hexcode or a boolean value that controls the stroke color or visibility of the marker stroke. Default: #C42127.
    - **fill-opacity**: A float value that controls the opacity of the fill. Default: 0.5.
    - **stroke-opacity**: A float value that controls the opacity of the stroke. Default: 1.0.

The names of all columns are **case sensitive**!

.. code-block:: python

        dwg.Map(chart_id="AbCd1").data(df)

List charts in a folder
==========================

This is particularly useful if you're editing a large number of charts and want to iterate through charts in a folder.

.. code-block:: python

        dwg.Folder(folder_id="12345").chart_list

=======================
CONTRIBUTING
=======================


=======================
CHANGELOG
=======================

- **v0.3.27**: Added all locator map icons.