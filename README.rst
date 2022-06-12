========================
Datawrapper Graphics
========================

A package that allows you to interface between your pandas dataframes and Datawrapper locator maps, charts, and folders in Python.


Installation
======================
Install using pip:
```pip install datawrappergraphics```

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

I want to...
==========================

Some simple usage patterns.

**Create a new chart.**

.. code-block:: python

        import datawrappergraphics as dwg

        dwg.Chart()

**Upload data to an existing chart.**

Data is uploaded as a pandas dataframe. Charts do not require any special columns, so go wild with it.

.. code-block:: python

        import datawrappergraphics as dwg

        dwg.Chart(chart_id="AbCd1").data(df)
