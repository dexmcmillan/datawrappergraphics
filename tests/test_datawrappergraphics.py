import pandas as pd
import datawrappergraphics
import os
import geopandas
import glob
import re
import numpy



TEST_MAP_ID = "rCSft"
TEST_CHART_ID = "W67Od"
TEST_HURRICANE_MAP_ID = "nSHo0"
EASTERN_UKRAINE_CHART_ID = "ioEie"

API_TEST_FOLDER = "105625"


test_map_data = pd.DataFrame({"title": ["Point 1"], "latitude": [50.2373819], "longitude": [-90.708556], "anchor": ["middle-right"], "tooltip": ["A test tooltip."], "icon": ["attention"]})

test_chart_data = pd.DataFrame({"date": pd.date_range("2022-01-01", "2022-06-02")[:50], "value": numpy.random.randint(1, 20, 50)})


# def test_create_chart():
    
#     assert (datawrappergraphics.Chart(folder_id=API_TEST_FOLDER)
#         .data(test_chart_data)
#         .head(f"TEST: Testing datawrappergraphics library's Chart class")
#         .deck(f"A test deck.")
#         .publish()
#     )
    
    
    

def test_simple_chart():
    
    assert (datawrappergraphics.Chart(chart_id=TEST_CHART_ID)
        .data(test_chart_data)
        .head(f"TEST: Testing datawrappergraphics library's Chart class")
        .deck(f"A test deck.")
        .publish()
        .move(folder_id=API_TEST_FOLDER)
    )



def test_simple_map():
    
    assert (datawrappergraphics.Map(chart_id=TEST_MAP_ID)
        .data(test_map_data)
        .head(f"TEST: Testing datawrappergraphics library")
        .deck(f"A test deck.")
        .move(folder_id=API_TEST_FOLDER)
    )



def test_export_chart():
    
    assert datawrappergraphics.Map(chart_id=TEST_MAP_ID).export()





# A more robust test to make sure the most complicated map - the Eastern Ukraine map - will work.
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
    areas["geometry"] = areas["geometry"].simplify(1)

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

    source_list_clean = set([item for sublist in source_list_clean for item in sublist if item]).append("Institute for the Study of War and AEI's Critical Threats Project")

    source_string = ", ".join(source_list_clean)

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
def test_hurricane_map():

    hurricane_map = (datawrappergraphics.StormMap(chart_id=TEST_HURRICANE_MAP_ID, storm_id="AL012022", xml_url="https://www.nhc.noaa.gov/nhc_at1.xml")
                    .data()
                    )
    
    hurricane_map = (hurricane_map
                    .head(f"TEST: Tracking {hurricane_map.storm_type.lower()} {hurricane_map.storm_name}")
                    .deck(f"Windspeed is currently measured at <b>{hurricane_map.windspeed} km/h</b>.")
                    .footer(source="U.S. National Hurricane Center")
                    .publish()
                    .move(API_TEST_FOLDER))
    
    assert hurricane_map



# def test_delete():
    
#     assert datawrappergraphics.Map(chart_id=TEST_CHART_ID).delete()
