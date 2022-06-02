# Datawrapper Graphics

A pythonic representation of Datawrapper graphics.

## Installation
Install directly from the github repository.
```pip install https://github.com/dexmcmillan/datawrappergraphics/releases/download/v0.1.33/datawrappergraphics-0.2.32-py3-none-any.whl```

## Usage
There are currently two main classes that can be implemented using this module:

* Map() - This is a datawrapper locator map.
* Chart() - This is a datawrapper chart.

Each of these classes inherits from the DatawrapperGraphic class, which is not meant to be implemented directly.

Classes can be implemented by using:

```
from datawrappergraphics.Map import Map

chart_id = "AbBe1"

map = (Map()
        .data()
        .head("A cool headline for your chart")
        .deck("A great looking deck, or subheadline, for your chart".)
        .footer("This is a note")
)
```