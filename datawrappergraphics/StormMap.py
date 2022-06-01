import pandas as pd
import geopandas
import pytz
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from datawrappergraphics.icons import dw_icons
from datawrappergraphics.Map import Map

# The StormMap class is a special extension of the Map class that takes data from the NOAA and turns
# it into a hurricane map with standard formatting. It takes one input: the storm ID of the hurricane
# or tropical storm that can be taken from the NOAA's National Hurricane Center.

# The NOAA stores this data in at least two separate zipfiles that need to be pulled in and processed.
class StormMap(Map):
    
    # Some variables that we want to be able to access when the class is instantiated.
    global storm_id
    global windspeed
    global storm_name
    global storm_type
    
    
    
    def __init__(self, storm_id: str, chart_id: str = None, copy_id: str = None):
        
        # Set storm id from the input given to the class constructor.
        self.storm_id = storm_id
        super().__init__(chart_id, copy_id)
    
    
    
    # This method gets the shapefile from the NOAA, which is in a zipfile.
    def __get_shapefile(self, filename, layer):
        
        # Download and open the zipfile.
        resp = urlopen(filename)
        
        # List out names of files in the zipfile.
        files = ZipFile(BytesIO(resp.read())).namelist()
        
        # Put it into a dataframe for easy iteration.
        files = pd.Series(files)

        file_name = files[files.str.contains(layer)].to_list()[0].replace(".shp", "")
        
        # Returns a geopandas df.
        return geopandas.read_file(filename, layer=file_name)
    
    
    
    
    # This function gets the total path of the hurricane, which is stored in a separate zip file entirely from the others.
    # TODO clean up this function ugh.
    def __total_path(self, storm_id):
        
        best_track_zip = f"https://www.nhc.noaa.gov/gis/best_track/{storm_id}_best_track.zip"
        total_path_points = self.__get_shapefile(best_track_zip, "pts.shp$")
        
        total_path_line = self.__get_shapefile(best_track_zip, "lin.shp$")

        total_path_points = total_path_points[total_path_points["STORMNAME"] == self.storm_name.upper()]
        total_path_points = total_path_points.rename(columns={"LAT": "latitude", "LON": "longitude"})

        total_path_points["longitude"] = total_path_points["geometry"].x.astype(float)
        total_path_points["latitude"] = total_path_points["geometry"].y.astype(float)
        total_path_points = total_path_points.drop(columns=["geometry"])
        
        for df in [total_path_points, total_path_line]:
            df["STORMTYPE"] = total_path_points["STORMTYPE"].replace({"TS": "S", "HU": "H", "TD": "D"})
            df = df[df["STORMTYPE"].isin(["D", "H", "S"])]

        total_path_points["type"] = "point"
        total_path_points["icon"] = "circle"
        total_path_points["STORMTYPE"]
        total_path_points["markerSymbol"] = total_path_points["STORMTYPE"]
        total_path_points["markerColor"] = total_path_points["markerSymbol"].replace({"D": "#567282", "S": "#567282", "H": "#e06618"})
        total_path_points["scale"] = 1.1
        total_path_points["tooltip"] = ""
        total_path_points["title"] = ""

        # total_path_points.loc[total_path_points["STORMTYPE"] == "D", "storm_type"] = "Depression"
        # total_path_points.loc[total_path_points["STORMTYPE"] == "H", "storm_type"] = "Hurricane"
        # total_path_points.loc[total_path_points["STORMTYPE"] == "S", "storm_type"] = "Storm"

        total_path_points["fill"] = "#C42127"
        
        
        
        total_path_line["type"] = "area"
        total_path_line["icon"] = "area"
        total_path_line["fill"] = "#C42127"
        total_path_line["stroke"] = "#000000"
        total_path_line["stroke-opacity"] = 1.0
        total_path_line["markerColor"] = "#C42127"
        total_path_line["fill-opacity"] = 0
        total_path_line["stroke-dasharray"] = "1,2.2"
        total_path_line["tooltip"] = ""
        total_path_line["title"] = ""
        
        # total_path_line = total_path_line[total_path_line["SS"] >= 1]
        
        total_path_line = total_path_line.dissolve(by='STORMNUM')
        
        
        return pd.concat([total_path_points, total_path_line])
    
    
    
    
    # This method is sort of like a custom version of Map's data() method, which is then called after calling this.
    
    # TODO add decorator to this to make it a "data" call, to match other maps?
    # TODO make it so this is called in the Map class's data() method so it instantiates like standard Map class.
    def process_data(self):
        
        # NOAA provides data in different timezomes (at least one: CST). Define eastern timezome here for later conversion.
        eastern = pytz.timezone('US/Eastern')
        
        # Get storm metadata.
        metadata = pd.read_xml("https://www.nhc.noaa.gov/nhc_ep1.xml", xpath="/rss/channel/item[1]/nhc:Cyclone", namespaces={"nhc":"https://www.nhc.noaa.gov"})
        
        # Split the marker for the center of the storm into latitude and longitude values.
        metadata["latitude"] = pd.Series(metadata.at[0, "center"].split(",")[0].strip()).astype(float)
        metadata["longitude"] = pd.Series(metadata.at[0, "center"].split(",")[1].strip()).astype(float)
        
        # Save windspeed in object variables.
        self.windspeed = metadata.at[0, "wind"].replace(" mph", "")
        self.windspeed = int(int(self.windspeed) * 1.60934)
        
        # Save name of storm in object variables.
        self.storm_name = metadata.at[0, "name"]
        
        # Save type of storm in object variables.
        self.storm_type = metadata.at[0, "type"]
        
        # Pull in data from NOAA five day forecast shapefile.
        five_day_latest_filename = f"https://www.nhc.noaa.gov/gis/forecast/archive/{self.storm_id}_5day_latest.zip"
        
        # Get points layer from five day forecast shapefile.
        points = self.__get_shapefile(five_day_latest_filename, "5day_pts.shp$")
        
        # Start by processing the points shapefile
        points["longitude"] = points["geometry"].x.astype(float)
        points["latitude"] = points["geometry"].y.astype(float)
        points = points.drop(columns=["geometry"])
        
        points["DATELBL"] = pd.to_datetime(points["DATELBL"]).apply(lambda x: x.tz_localize("America/Chicago"))
        points["DATELBL"] = points["DATELBL"].dt.tz_convert('US/Eastern')
        points["type"] = "point"
        points["icon"] = "circle"
        points["fill"] = "#C42127"
        points["title"] = points['DATELBL'].dt.strftime("%b %e") + "<br>" + points['DATELBL'].dt.strftime("%I:%M %p")
        points["title"] = points["title"].str.replace("<br>0", "<br>")
        points["scale"] = 1.1
        points["markerSymbol"] = points["DVLBL"]
        points["markerColor"] = points["markerSymbol"].replace({"D": "#567282", "S": "#567282", "H": "#e06618"})
        
        points.loc[points["DVLBL"] == "D", "storm_type"] = "Depression"
        points.loc[points["DVLBL"] == "H", "storm_type"] = "Hurricane"
        points.loc[points["DVLBL"] == "S", "storm_type"] = "Storm"
        
        points["tooltip"] = "On " + points['DATELBL'].dt.strftime("%b %e") + " at " + points['DATELBL'].dt.strftime("%I:%M %p").str.replace("$0", "", regex=True) + " EST, the storm is projected to be classified as a " + points["storm_type"].str.lower() + "."
        points["tooltip"] = points["tooltip"].str.replace(" 0", " ")
        
        # Get center line layer from five day forecast shapefile.
        centre_line = self.__get_shapefile(five_day_latest_filename, "5day_lin.shp$")
        
        # Define properties unique to centre line.
        centre_line["fill"] = "#C42127"
        centre_line["stroke"] = "#000000"
        centre_line["markerColor"] = "#C42127"
        centre_line["fill-opacity"] = 0.0
        
        # Get probable path layer from five day forecast shapefile.
        probable_path = self.__get_shapefile(five_day_latest_filename, "5day_pgn.shp$")
        
        # Define properties unique to probable path shape.
        probable_path["fill"] = "#6a3d99"
        probable_path["stroke"] = "#000000"
        probable_path["markerColor"] = "#6a3d99"
        probable_path["fill-opacity"] = 0.2
        probable_path["stroke-opacity"] = 0
        
        # Define some common style points for the centre line and the probable path.
        for df in [centre_line, probable_path]:
        
            df["type"] = "area"
            df["icon"] = "area"
        
        # Call the method that returns our total path information. This holds historical info about where the hurricane has been.
        total_path = self.__total_path(storm_id=self.storm_id)
        
        # Concatenate all our dataframes into one large dataframe so we can upload it.
        all_shapes = pd.concat([centre_line, probable_path, points, total_path])
        
        # Filter out all the columsn we don't care about keeping.
        # TODO remove this, as the new data() method should be able to do this without specifying.
        all_shapes = all_shapes[["markerColor", "fill", "fill-opacity", "stroke", "stroke-opacity", "type", "icon", "latitude", "longitude", "geometry", "title", "tooltip", "scale", "markerSymbol", "stroke-dasharray"]]
        
        # Fill any null values in latitude and longitude columns.
        # TODO do we need these fillna lines?
        all_shapes["latitude"] = all_shapes["latitude"].fillna("")
        all_shapes["longitude"] = all_shapes["longitude"].fillna("")
        
        # Do the same for other values so we don't send any null values.
        for col in ["markerColor", "fill", "fill-opacity", "stroke", "type", "icon", "title", "tooltip", "scale", "markerSymbol"]:
            all_shapes[col] = all_shapes[col].fillna("")
          
        # I've commented the next line out because I don't think I need it with the new data() method structure.  
        # all_shapes["stroke-dasharray"] = all_shapes["stroke-dasharray"].fillna("100000")

        # Save as the object's dataset.
        self.dataset = all_shapes
        
        # Return self so we can chain methods.
        return self