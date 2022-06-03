# Datawrapper Graphics

A pythonic representation of Datawrapper graphics that takes pandas Dataframes as input for charts and locator maps.

[![GitHub issues](https://img.shields.io/github/issues/Naereen/StrapDown.js.svg)](https://github.com/dexmcmillan/datawrappergraphics/issues)

[![Latest release](https://badgen.net/github/release/Naereen/Strapdown.js)](https://github.com/dexmcmillan/datawrappergraphics/releases/tag/v0.2.35)



## Installation
Install directly from the github repository.
```pip install https://github.com/dexmcmillan/datawrappergraphics/releases/download/v0.1.33/datawrappergraphics-0.2.32-py3-none-any.whl```

## Usage
There are currently two main classes that can be implemented using this module:

* Map - This is a datawrapper locator map.
* Chart - This is a datawrapper chart.

Each of these classes inherits from the DatawrapperGraphic class, which is not meant to be implemented directly.

### Methods

Map and Chart classes have several methods that can be chained, one after another, to build out your chart.

**data(data)**

Your dataframe needs to have the following columns:

* 

**head(text)**

**deck(data)**

**footer(data)**

**move()**

**export()**

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
