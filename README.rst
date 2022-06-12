========================
Datawrapper Graphics
========================

A package that allows you to interface between your pandas dataframes and Datawrapper locator maps, charts, and folders in Python.

======================
Installation
======================
Install using pip:
```pip install datawrappergraphics```

====================
Usage
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
Guide
==========================

Some simple usage patterns. Get started by importing the package:

.. code-block:: python

        import datawrappergraphics as dwg

Create a new chart.
==========================

.. code-block:: python

        dwg.Chart()

Upload data to an existing chart.
==========================

Data is uploaded as a pandas dataframe. Charts do not require any special columns, so go wild with it.

.. code-block:: python

        dwg.Chart(chart_id="AbCd1").data(df)

Upload data to an existing locator map
==========================

The Map class is used to interact with locator map data. Your dataframe has to have a few required columns:
- Type: Either "point" or "area", depending on whether the row is a point marker or an area.
- latitude/longitude or geometry: Point markers use two columns to locate: latitude and longitude. Area markers need a geometry column with WKT in the rows.

.. code-block:: python

        dwg.Map(chart_id="AbCd1").data(df)

List charts in a folder
==========================

This is particularly useful if you're editing a large number of charts and want to iterate through charts in a folder.

.. code-block:: python

        dwg.Folder(folder_id="12345").chart_list
