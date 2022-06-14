import pandas as pd
import datawrappergraphics
from datawrappergraphics.errors import *
import os
import geopandas
import glob
import re
import numpy
import requests
import json
import logging
import pytest


TEST_MAP_ID = "rCSft"
TEST_CHART_ID = "W67Od"
TEST_HURRICANE_MAP_ID = "nSHo0"
EASTERN_UKRAINE_CHART_ID = "ioEie"
TEST_FIRE_MAP = "HqkeQ"
TEST_FIB_CHART = "FAEyt"
TEST_CIRCLE_CHART = "9iLF3"
TEST_CALENDAR_MONTH_CHART = "XTqN8"
TEST_CALENDAR_YEAR_CHART = "b7HuL"

API_TEST_FOLDER = "105625"

test_map_data = pd.DataFrame({"title": ["Point 1"], "latitude": [50.2373819], "longitude": [-90.708556], "anchor": ["middle-right"], "tooltip": ["A test tooltip."], "icon": ["circle"], "type": ["point"]})
test_chart_data = pd.DataFrame({"date": pd.date_range("2022-01-01", "2022-06-02")[:50], "value": numpy.random.randint(1, 20, 50)})
test_circle_chart_data = pd.DataFrame({"month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "value": numpy.random.randint(1, 20, 12)})
test_calendar_month_chart_data = pd.DataFrame({"date": pd.date_range("2022-09-01", "2022-10-31"), "value": numpy.random.randint(1, 20, 61)})
test_calendar_year_chart_data = pd.DataFrame({"date": pd.date_range("2022-01-01", "2022-12-31")})
test_calendar_year_chart_data["value"] = numpy.random.randint(1, 20)


@pytest.mark.folder
def test_get_folder():
    assert datawrappergraphics.Folder(API_TEST_FOLDER).chart_list



@pytest.mark.special
def test_calendar_chart():
    
    month_chart = (datawrappergraphics.CalendarChart(TEST_CALENDAR_MONTH_CHART)
                   .data(test_calendar_month_chart_data, date_col="date", timeframe="month")
                   .head(f"TEST: Calendar (month) chart test graphic")
                   .publish()
                   )
    
    year_chart = (datawrappergraphics.CalendarChart(TEST_CALENDAR_YEAR_CHART)
                  .data(test_calendar_year_chart_data, date_col="date", timeframe="year")
                  .head(f"TEST: Calendar (year) chart test graphic")
                  .publish()
                  )
    
    assert month_chart, year_chart


def test_load_wrong_chart():
    try: datawrappergraphics.Map(TEST_CHART_ID)
    except WrongGraphicTypeError: assert True


@pytest.mark.special
def test_fibonacci_spiral():
    fib_chart = datawrappergraphics.FibonacciChart(TEST_FIB_CHART).data(test_chart_data).head(f"TEST: Fibonacci spiral test graphic").publish()
    
    logging.info(fib_chart.metadata)
    
    
    
    
    
@pytest.mark.special
def test_circle_chart():
    datawrappergraphics.CircleChart(TEST_CIRCLE_CHART).data(test_circle_chart_data).head(f"TEST: Circle chart test graphic").publish()


@pytest.mark.quick
def test_wrong_chart_type():
    
    wrong_type = datawrappergraphics.Chart(chart_type="laksfd").delete()
    right_type = datawrappergraphics.Chart(chart_type="d3-bars").delete()
    
    assert wrong_type and right_type


def test_wrong_hexcode():
    data = test_map_data.copy()
    data["fill"] = "a color!"
    data["type"] = "point"
    
    
    try: datawrappergraphics.Map(chart_id=TEST_MAP_ID).data(data)
    except InvalidHexcodeError: assert True


# def test_create_chart():
    
#     assert (datawrappergraphics.Chart(folder_id=API_TEST_FOLDER)
#         .data(test_chart_data)
#         .head(f"TEST: Testing datawrappergraphics library's Chart class")
#         .deck(f"A test deck.")
#         .publish()
#     )
    
    
    
@pytest.mark.quick
def test_simple_chart():

    chart = datawrappergraphics.Chart(chart_id=TEST_CHART_ID)
    
    chart.metadata["metadata"]["visualize"]["custom-colors"] = {"value": "#cccccc"}
    
    chart =  (chart
        .data(test_chart_data)
        .head(f"TEST: Testing datawrappergraphics library's Chart class")
        .deck(f"A test deck.")
        .publish()
        .move(folder_id=API_TEST_FOLDER)
    )

    logging.info(chart.metadata)
    
    assert chart


@pytest.mark.quick
@pytest.mark.maps
def test_simple_map():
    
    simple_map = datawrappergraphics.Map(chart_id=TEST_MAP_ID)
    
    
    
    simple_map = (simple_map
        .data(test_map_data)
        .head(f"TEST: Testing datawrappergraphics library")
        .deck(f"A test deck.")
        .move(folder_id=API_TEST_FOLDER)
        )
    
    
    assert simple_map

# This test changes the metadata in a test chart and update the live chart.
@pytest.mark.quick
def test_metadata():
    chart = datawrappergraphics.Map(chart_id=TEST_MAP_ID)
    
    before = chart.metadata["metadata"]["describe"]["source-name"]
    
    logging.info(chart.metadata)
    
    chart.metadata["metadata"]["describe"]["source-name"] = "".join([str(x) for x in numpy.random.randint(0, 9, 5)])
    
    chart.set_metadata()
    
    after = chart.metadata["metadata"]["describe"]["source-name"]
    
    logging.info(f"Before: {before}. After: {after}")
    
    assert before != after



# def test_export_chart():
    
#     assert datawrappergraphics.Map(chart_id=TEST_MAP_ID).export()





# A more robust test to make sure the most complicated map - the Eastern Ukraine map - will work.
@pytest.mark.maps
def test_ukraine_map():

    # Bring in and process shapefile data for Russian advances.

    all_files = glob.glob(os.path.join("./tests/assets/ukraineadvance", "*.zip"))

    li = []

    # Loop through each file and append to list for concat.
    for filename in all_files:
        df = geopandas.read_file(filename)
        df["layer"] = re.search("\\\\[a-zA-Z0-9]+\.", filename)[0]
        df["layer"] = df["layer"].str.replace(".", "", regex=True).str.replace("\\", "", regex=True)
        li.append(df)

    # Concatenate all shape dataframes together.
    areas = pd.concat(li, axis=0, ignore_index=True)

    # Filter out any files we don't want included.
    areas = areas.loc[~areas["layer"].isin(["ClaimedRussianTerritoryinUkraine", "ClaimedUkrainianCounteroffensives"]),:]

    # Define colour for each of the layers (not all of these are included in the import).
    areas.loc[areas["layer"].str.contains("ClaimedRussianTerritoryinUkraine"), "markerColor"] = "grey"
    areas.loc[areas["layer"].str.contains("ClaimedUkrainianCounteroffensives"), "markerColor"] = "#1f78b4"
    areas.loc[areas["layer"].str.contains("UkraineControl"), "markerColor"] = "#c42127"
    areas.loc[areas["layer"].str.contains("AssessedRussianAdvances"), "markerColor"] = "#f8c325"

    # Define type for area markers.
    areas["type"] = "area"

    # Define opacity for area markers.
    areas["fill-opacity"] = 0.2

    # Define fill and stroke colours.
    areas["fill"] = areas["markerColor"]
    areas["stroke"] = areas["markerColor"]

    # Define title.
    areas["title"] = areas["layer"]

    # Define icon type, which may actually not be necessary!
    areas["icon"] = "area"

    # Simplify the geometry so it's under 2MB for import into Datawrapper.
    areas["geometry"] = areas["geometry"].simplify(2)

    # Dissolve so there are only as many shapes as there are files.
    areas = areas.dissolve(by="layer")

    # Filter out columns we don't need for the visualization.
    areas = areas[["title", "geometry", "fill", "stroke", "type", "icon", "fill-opacity"]]

    ## Import sheet data of points.
    raw = (pd
        .read_csv("https://docs.google.com/spreadsheets/d/17RIbkQI6o_Y_NZalfqZvB8n_j_AmTV5GoNMuzdbkw3w/export?format=csv&gid=0", encoding="utf-8")
        .dropna(how="all", axis=1)
        )

    ## Rename columns from the spreadsheet.
    raw.columns = ["title", "tooltip", "source", "hide_title", "visible", "coordinates", "anchor", "icon"]

    ## Clean data.
    points = (raw
            .dropna(how="all")
            .set_index("title")
            .reset_index()
            .loc[raw["visible"] == True]
            )

    # Set anchor based on what's specified in spreadsheet.
    points["anchor"] = points["anchor"].str.lower()

    # Build the tooltip for display.
    points["tooltip"] = points["tooltip"].str.strip()
    points["tooltip"] = '<b>' + points["title"] + '</b><br>' + points["tooltip"] + ' <i>(Source: ' + points["source"].fillna("").str.strip().str.replace("\"", "'") + ')</i>'

    # Define default marker colour for these points.
    points["markerColor"] = "#29414F"

    # Define default marker type.
    points["type"] = "point"

    # Define default icon type.
    points["icon"] = 'city'

    # Define default scale for points.
    points["scale"] = 1.2

    # Define lat/long for point values.
    points["longitude"] = points["coordinates"].apply(lambda x: x.split(", ")[0].replace("[", ""))
    points["latitude"] = points["coordinates"].apply(lambda x: x.split(", ")[1].replace("]", ""))

    # Specify different marker type for capital city.
    points.loc[points["title"] == "Kyiv", "icon"] = "star-2"

    # Prepare source string from source column.
    points["source"] = points["source"].fillna("")

    source_list = set(points["source"].to_list())
    source_list_clean = []
    for entry in source_list:
        try:
            word = entry.split(", ")
            source_list_clean.append(word)
        except:
            pass

    source_list_clean = set([item for sublist in source_list_clean for item in sublist if item])

    source_string = ", ".join(source_list_clean) + ", " + "Institute for the Study of War and AEI's Critical Threats Project"

    # We only want these cities to show up on the Eastern Ukraine map.
    eastern_cities = ["Kyiv", "Kharkiv", "Izyum", "Mariupol", "Severodonetsk", "Mykolaiv", "Kherson", "Odesa", "Lyman"]

    # Bring together points and shapes for import into Datawrapper map.
    data = pd.concat([areas, points[points["title"].isin(eastern_cities)]])
    
    (datawrappergraphics.Map(chart_id=EASTERN_UKRAINE_CHART_ID)
                .data(data, append="./tests/assets/shapes/shapes-easternukrainemap.json")
                .head(f"TEST: Russia launches offensive in Eastern Ukraine")
                .deck("Tap or hover over a point to read more about fighting in that area.")
                .footer(note=f"Source: {source_string}.", byline="Wendy Martinez, Dexter McMillan")
                .publish()
            )
    


# A note that this test will work only until the storm ID is relevant. The data disappears once the storm has passed.
@pytest.mark.maps
def test_hurricane_map():

    hurricane_map = (datawrappergraphics.StormMap(chart_id=TEST_HURRICANE_MAP_ID, storm_id="EP022022", xml_url="https://www.nhc.noaa.gov/nhc_ep2.xml")
                    .data()
                    )
    
    hurricane_map = (hurricane_map
                    .head(f"TEST: Tracking {hurricane_map.storm_type.lower()} {hurricane_map.storm_name}")
                    .deck(f"Windspeed is currently measured at <b>{hurricane_map.windspeed} km/h</b>.<br><br>The dotted line shows the historical path of the weather system.")
                    .footer(source="U.S. National Hurricane Center")
                    .publish()
                    .move(API_TEST_FOLDER))
    
    assert hurricane_map

@pytest.mark.maps
def test_firemap():

    r = requests.get("https://services.arcgis.com/Eb8P5h4CJk8utIBz/ArcGIS/rest/services/Active_Wildfire_Locations/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=standard&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&defaultSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token=")

    data = geopandas.read_file(json.dumps(r.json()))
    data = data.drop(columns="ID")
    print(data)

    data["markerColor"] = data["FIRE_STATUS"].replace({"Under Control": "#436170",
                                                    "New": "#F8C325",
                                                    "Out of Control": "#c42127",
                                                    "Being Held": "#000000",
                                                    "Assistance Started": "#1F78B4"
                                                    })

    data["type"] = "point"
    data["icon"] = "fire"

    avg = data["AREA_ESTIMATE"].min()
    std = data["AREA_ESTIMATE"].std()

    data["scale"] = ((data["AREA_ESTIMATE"] - avg) / (std)) + 1
    data["scale"] = data["scale"].apply(lambda x: 2.2 if x > 2.2 else x)

    data["tooltip"] = "<big>" + data['RESP_AREA'] + "</big><br><b>Status</b>: " + data['FIRE_STATUS'] + "</span>" + "<br><b>Cause</b>: " + data["GENERAL_CAUSE"] 
    data = data.sort_values("scale")

    percent_under_control = round(len(data[data['FIRE_STATUS'] == 'Under Control'])/len(data)*100, 0)

    assert (datawrappergraphics.Map(chart_id=TEST_FIRE_MAP)
                .data(data, "./tests/assets/shapes/shapes-abfiremap.json")
                .head(f"TEST: There are <b>{len(data)} wildfires</b> burning across Alberta")
                .deck(f"As of today, {percent_under_control}% are listed as under control.")
                .footer(source="Government of Alberta")
                .publish()
                )

# def test_delete():
    
#     assert datawrappergraphics.Map(chart_id=TEST_CHART_ID).delete()
