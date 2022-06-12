========================
Datawrapper Graphics
========================

A pythonic representation of Datawrapper graphics that takes pandas Dataframes as input for charts and locator maps.

[![Latest release](https://badgen.net/github/release/Naereen/Strapdown.js)](https://github.com/dexmcmillan/datawrappergraphics/releases/download/v0.3.2/datawrappergraphics-0.3.24-py3-none-any.whl)



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

```
import datawrappergraphics

chart_id = "AbBe1"

map = (Map()
        .data(aPandasDataframe)
        .head("A cool headline for your chart")
        .deck("A great looking deck, or subheadline, for your chart".)
        .footer("This is a note")
)
```
