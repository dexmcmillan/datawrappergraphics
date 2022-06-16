import requests
import json
import os
import sys
import re
import pandas as pd
import geopandas
import datetime
import logging
import urllib.error
import numpy as np
import math
from geojson import Feature
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from datawrappergraphics.icons import dw_icons
from datawrappergraphics.errors import *
from IPython.display import HTML
from io import StringIO
from shapely.geometry import shape, Point


class Datawrapper:
    
    """The base class for Datawrapper folders and graphics.
    
    This holds methods that are general to interacting with Datawrapper's API, like the authentication method. This object should not be instantiated directly.
    
    Args:
        auth_token (str, optional): The auth_token from Datawrapper. You can authenticate by passing this into the class instantiation, or by putting an auth.txt file in your project's root folder with the token.

    Attributes:
        DW_AUTH_TOKEN (str): Token to authenticate to Datawrapper's API.
        path (str): Path that the script is running from using this module.
        script_name (str): Name of the script currently running using this module.
        _os_name (str): What operating system the script is running on.
    """
    
    global DW_AUTH_TOKEN
    global path
    global script_name
    global _os_name
    
    def __init__(self,
                 auth_token: str = None):
        
        # Authenticate to datawrapper's API.
        self.auth(token=auth_token)
        
        
        # Set OS name (see global Graphic variables)
        self._os_name = os.name
        
        self.script_name = os.path.basename(sys.argv[0]).replace(".py", "")
        
        self.path = os.path.dirname(sys.argv[0]) 
    
    
    # This method authenticates to Datawrapper and returns the token for accessing the DW api.
    def auth(self, token: str = None):
        
        """A mostly internal function to authenticate to Datawrapper's API.

        Args:
            token (str): If a token is specified manually, it can be passed here.

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        if token != None:
            DW_AUTH_TOKEN = token
        else:
            # On a local machine, it will read the auth.txt file for the token.
            try:
                with open('./auth.txt', 'r') as f:
                    DW_AUTH_TOKEN = f.read().strip()
            # If this is run using Github actions, it will take a secret from the repo instead.
            except FileNotFoundError:
                try: DW_AUTH_TOKEN = os.environ['DW_AUTH_TOKEN']
                except: raise Exception(f"No auth.txt file found, and no environment variable specified for DW_AUTH_TOKEN. Please add one of the two to authenticate to Datawrapper's API.")
        
        self.DW_AUTH_TOKEN = DW_AUTH_TOKEN    
        return self 




class Folder(Datawrapper):
    
    """The base class for a Datawrapper folder.
    
    
    Args:
        folder_id (str): The ID of the folder.

    Attributes:
        folder_id (str): The id of the folder fetched.
        chart_list (list): A list of charts in the folder.
        num_charts (int): The number of charts in this folder.
        
    Returns:
        object: A datawrapper Folder object.
    """
    
    global folder_id
    global num_charts
    global chart_list
    
    def __init__(self,
                 folder_id: str,
                 *args,
                 **kwargs):
        
        super(Folder, self).__init__(*args, **kwargs)
        
        # Set folder ID from arg.
        self.folder_id = folder_id
        self.num_charts = len(self.folder_id)
        
        # Run a small funtion to collect the chart IDs of charts in the folder.
        self.chart_list = self._get_chart_list()
        
        
        
        
    def _get_chart_list(self):
        
        headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }
        
        r = requests.get(f"https://api.datawrapper.de/v3/charts?folderId={self.folder_id}&order=DESC&orderBy=createdAt&offset=0&expand=true", headers=headers)
        
        if r.ok: return [obj["publicId"] for obj in r.json()["list"]]
        else: raise Exception(f"Couldn't fetch charts. Response: {r.reason}")



class Graphic(Datawrapper):
    
    """The base class for Datawrapper graphics.
    
    There are two opens when creating a new Graphic object:
        
    1. You can create a brand new chart by specifying no chart_id and no copy_id. This is not recommended but can be used to create a large number of charts en-mass,
    and then save their info into a csv or something.
    
    2. You can specify a copy_id, and a new chart will be created by copying that chart. This is also not recommended but can be used for various purposes.
    
    3. You can specify a chart that is already made that you want to update. This is the easiest way - copy another chart in the Datawrapper app and then
    use that chart_id.
    
    Args:
        chart_id (str): The ID of the chart you're bringing into the module. Providing this string value is the typical implementation of this library.
        copy_id (str, optional): Instead of a chart_id, you can specify the id of a chart to copy. Keep in mind that this will keep making copies if you keep running code, so it's best run only once, then use chart_id.
        auth_token (str, optional): The auth_token from Datawrapper. You can authenticate by passing this into the class instantiation, or by putting an auth.txt file in your project's root folder with the token.
        folder_id (str, optional): If a new chart is being created because no chart_id or copy_id is passed, this is where you specify which folder to create it in.

    Attributes:
        CHART_ID (str): The CHART_ID is a unique ID that can be taken from the URL of datawrappers. It's required to use the DW api.
        metadata (str): Holds the chart's metadata when the graphic is instantiated.
        dataset (pd.DataFrame): Represents the data that is uploaded or will be uploaded to the graphic.
        DW_AUTH_TOKEN (str): Token to authenticate to Datawrapper's API.
        path (str): Path that the script is running from using this module.
        script_name (str): Name of the script currently running using this module.
        
    Returns:
        object: Returns self, the instance of the Graphic class. Can be chained with other methods.
    """
    
    global CHART_ID
    global metadata
    global dataset
    global allowed_chart_types
    
    def __init__(self,
                 chart_id: str = None,
                 copy_id: str = None,
                 folder_id: str = None,
                 chart_type: str = None):
        
        
        # Turn on logging of INFO level.
        logging.basicConfig(level=logging.INFO)
        
        
        super(Graphic, self).__init__()
        
        self.allowed_chart_types = [
                "d3-bars",
                "d3-bars-split",
                "d3-bars-stacked",
                "d3-bars-bullet",
                "d3-dot-plot",
                "d3-range-plot",
                "d3-arrow-plot",
                "column-chart",
                "grouped-column-chart",
                "stacked-column-chart",
                "d3-area",
                "d3-lines",
                "d3-pies",
                "d3-donuts",
                "d3-multiple-pies",
                "d3-multiple-donuts",
                "d3-scatter-plot",
                "election-donut-chart",
                "tables",
                "d3-maps-choropleth",
                "d3-maps-symbols",
            ]
        
        # Define common headers for all the below options for instantiating Datawrapper graphics.
        headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }
        
        # If no chart ID is passed, and no copy id is passed, we create a new chart from scratch.
        if chart_id == None and copy_id == None:
            
            logging.info(f"No chart specified. Creating new chart...")
            
            # If a folder is specified in which to create the chart, handle that here.
            if folder_id:
                payload = {"folderId": folder_id}
                
            # Otherwise, just send an empty payload.    
            else:
                
                if chart_type in self.allowed_chart_types + ["locator-map"]:
                    payload = {"type": chart_type}
                else:
                    logging.warning(f"Invalid or no chart type specified. Creating new chart as a line chart instead.")
                    payload = {"type": "d3-lines"}
            
            response = requests.post(f"https://api.datawrapper.de/v3/charts/", json=payload, headers=headers)
            chart_id = response.json()["publicId"]

            logging.info(f"New chart created with id {chart_id}")
            
            self.CHART_ID = chart_id
        
        # If we want to make a copy of a graphic to create the new graphic.    
        elif chart_id == None and copy_id != None:
            
            logging.info(f"No chart specified. Copying chart with ID: {copy_id}...")
            
            response = requests.post(f"https://api.datawrapper.de/v3/charts/{copy_id}/copy", headers=headers)
            chart_id = response.json()["publicId"]
            
            logging.info(f"New chart ({chart_id}) created as a copy of {copy_id}.")
            
            self.CHART_ID = chart_id
            
        # If we specify a chart id and no copy id, then there is a chart already made that we're altering.    
        elif chart_id != None and copy_id == None:
            
            self.CHART_ID = chart_id
        
        # Throw exception if both copy id and chart id are input.
        elif chart_id != None and copy_id != None:
            raise Exception(f"Please specify either a chart_id or a copy_id, but not both.")

        # Same for metadata.
        self.metadata = self._get_metadata()

    
    
    
    
    def _check_graphic_type(self, input_type: str | list):
        
        """Checks if the graphic is the right type to be loaded into a class.
        
        Args:
            input_type (str): The type of graphic to validate.
            
        Returns:
            bool: Returns True if it's a valid map type, otherwise raises an error.
        """
        
        if isinstance(input_type, str):
            input_type = [input_type]
            
        type = self.metadata["type"]
        
        if type in input_type:
            return True
        
        else:
            raise WrongGraphicTypeError(type)
    
    
    
    
    
    def show(self):
        
        """Returns an HTML Iframe of the datawrapper chart for showing in Jupyter notebooks.
        
        Args:
            None
            
        Returns:
            HTML: Returns HTML that can be loaded in Jupyter notebook output.
        """
        
        iframe_code = self.metadata["metadata"]["publish"]["embed-codes"]["embed-method-iframe"]
        
        return HTML(iframe_code)
    
    
        
    
    def _get_metadata(self):
        
        """Used to collect data for the chart.
        
        This method is used on init to collect all the data (not just what's in the metadata object, but ALL the data from the chart)
        into in the object for reference in the metadata property.
        
        Note that it will not (as of yet) update on the live chart until you call set_metadata().
        
        Args: None
        """
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }
        
        r = requests.get(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}", headers=headers)
        
        metadata = r.json()
        
        if r.ok: return metadata
        else: raise Exception(f"Couldn't update metadata. Response: {r.reason}")
        
        
    
    
    
    
    
    
    def set_metadata(self):
        
        """A method that sends the metadata stored in the Graphics object to the live chart on Datawrapper.

        Args: None

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }
        
        r = requests.patch(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}", headers=headers, data=json.dumps(self.metadata).encode('utf-8'))
        
        self.metadata = r.json()
        
        if r.ok: logging.info(f"SUCCESS: Metadata updated.")
        else: raise Exception(f"Couldn't update metadata. Response: {r.reason}")
        
        return self
    
    
    
    
    
    
    # Add the chart's headline.
    def head(self, string: str):
        
        """Updates the title -- or headline -- of your graphic.

        Args:
            string (str): The headline for your chart.

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
    
        # Define headers for headline upload.
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }
        
        # Take the string input as a parameter and put it into a payload object. Then convert to JSON string.
        data = {"title": string}
        data = json.dumps(data)
        
        r = requests.patch(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}", headers=headers, data=data.encode('utf-8'))
        
        if r.ok: logging.info(f"SUCCESS: Chart head added.")
        else: raise Exception(f"ERROR: Chart head was not added. Response: {r.text}")
        
        return self
    
    
    
    
    
    
    

    
    def deck(self, deck: str):
        
        """Updates the deck -- or subheader -- of your graphic.

        Args:
            string (str): The subhead for your chart.

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        headers = {
            "Accept": "*/*", 
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }
        
        payload =  {
            "metadata": {
                "describe": {
                    "intro": deck,
                },
            }
        }
        
        r = requests.patch(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}", headers=headers, data=json.dumps(payload).encode('utf-8'))
        
        if r.ok: logging.info(f"SUCCESS: Chart deck added.")
        else: raise Exception(f"ERROR: Chart deck was not added. Response: {r.text}")
        
        # Update the object's metadat representation.
        self.metadata = r.json()
        
        return self
    
    
    
    
    
    
    
    
    
    ## Adds a timestamp to the "notes" section of your chart. Also allows for an additional note string that will be added before the timestamp.
    
    def footer(self, source: str = None, byline:str = "Dexter McMillan", note: str = "", timestamp: bool = True):
        
        """Updates the footer info of your graphic.

        Args:
            source (str): The graphic's source.
            byline (str): The graphic's byline.
            note (str): The graphic's note (showing at the bottom of the graphic).
            timestamp (bool): Whether a timestamp should be included or not. Timestamps are added right after whatever you specify as the note.

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        today = datetime.datetime.today()
        
        if self._os_name == "posix":
            today = today - datetime.timedelta(hours=4)
        
        # Get day and time strings for use in the footer timestamp.
        time = today.strftime('%I:%M') + " " + ".".join(list(today.strftime('%p'))).lower() + "."
        day = today.strftime('%B %d, %Y')
        
        # Use day and time values and create the string we put into the footer as a timestamp.
        timestamp_string = f"Last updated on {day} at {time}".replace(" 0", " ")
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }
        
        # This is a template object for the structure of the patch payload that Datawrapper API accepts.
        data =  {
            "metadata": {
                "describe": {
                    "source-name": source,
                    "byline": byline,
                },
                "annotate": {
                    "notes": f"{note} {timestamp_string if timestamp else ''}".strip(),
                },
            }
        }

        # Make the HTTP request to update metadata.
        r = requests.patch(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}", headers=headers, data=json.dumps(data))
        
        if r.ok: logging.info(f"SUCCESS: Chart footer (byline, notes, and source) built and added.")
        else: raise DatawrapperAPIError(f"ERROR: Couldn't build chart footer. Response: {r.reason}")
        
        # Update the object's metadat representation.
        self.metadata = r.json()
        
        return self
    
    
    
    
    
    
    
    
    
    def publish(self):
        
        """Publishes your graphic. Is typically called last in an implementation pattern.

        Args:
            None

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """

        headers = {
            "Accept": "*/*", 
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }

        r = requests.post(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/publish", headers=headers)
        
        if r.ok: logging.info(f"SUCCESS: Chart published!")
        else: raise DatawrapperAPIError(f"ERROR: Chart couldn't be published. Response: {r.reason}")
        
        return self
    
    
    
    
    
    def unpublish(self):
        
        """Unpublishes your graphic.

        Args:
            None

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """

        headers = {
            "Accept": "*/*", 
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }

        r = requests.post(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/unpublish", headers=headers)
        
        if r.ok: logging.info(f"SUCCESS: Chart unpublished.")
        else: raise DatawrapperAPIError(f"ERROR: Chart couldn't be unpublished. Response: {r.reason}")
        
        return self
    
    
    

    
    
    
    
    # Moves your chart to a particular folder ID.
    def move(self, folder_id: str):
        
        """Moves your graphic to the specified folder ID.

        Args:
            folder_id (str): The folder to move your chart to.

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        headers = {
            "Accept": "*/*", 
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }
        
        payload = {
            "ids": [self.CHART_ID],
            "patch": {"folderId": folder_id}
            }

        r = requests.patch(f"https://api.datawrapper.de/v3/charts", json=payload, headers=headers)
        
        if r.ok: logging.info(f"SUCCESS: Chart moved to folder ID {folder_id}!")
        else: raise DatawrapperAPIError(f"ERROR: Chart couldn't be moved. Response: {r.reason}")
        
        return self
    
    
    
    
    
    
    def delete(self):
        
        """Deletes your graphic.

        Args:
            None

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        logging.warning(f"Deleting chart with ID {self.CHART_ID}!")
        
        headers = {
            "Accept": "*/*", 
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }

        r = requests.delete(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}", headers=headers)
        
        if r.ok: logging.info(f"SUCCESS: Chart published!")
        else: raise DatawrapperAPIError(f"ERROR: Chart couldn't be deleted. Response: {r.reason}")
        
        return self
    
    
    
    
    def export(self, format: str = "png", filename: str = "export"):
        
        """Exports your graphic.

        Args:
            format (str, optional): The filetype to export as. Allowed types: png, svg.
            filename (str, optional): The name for the exported file, relative to project root. Defaults to: export.png. Do not specify a file suffix here.

        Returns:
            object: Returns self, the instance of the Graphics class. Can be chained with other methods.
        """
        
        VALID_FORMAT_LIST = ["png", "svg"]
        
        if format not in VALID_FORMAT_LIST:
            raise InvalidExportTypeError(f"Invalid export type specified.", VALID_FORMAT_LIST)
        
        file_path = self.path + filename + "." + format
        
        headers = {
            "Accept": "image/png", 
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }

        export_chart_response = requests.get(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/export/{format}?unit=px&mode=rgb&plain=false&scale=1&zoom=2&download=true&fullVector=false&ligatures=true&transparent=false&logo=auto&dark=false", headers=headers)
            
        
        if export_chart_response.ok:
            logging.info(f"SUCCESS: Chart with ID {self.CHART_ID} exported and saved!")
            
            with open(file_path, "wb") as response:
                response.write(export_chart_response.content)
                
        else: raise DatawrapperAPIError(f"ERROR: Chart couldn't be exported as {format}. Response: {export_chart_response.reason}")
        
        return self





class Chart(Graphic):
    
    """Defines methods and variables for uploading data to datawrapper charts (scatter plots, tables etc).
    
    Use this class to create a new, copy, or to manage a currently existing Datawrapper chart (ie. not a map!).
    
    """
    
    def __init__(self,
                 *args,
                 **kwargs
                 ):
        
        super(Chart, self).__init__(*args, **kwargs)
        
        self._check_graphic_type(self.allowed_chart_types)
        
        headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }
        
        # Grab data from already existing chart and store it in this object.
        r = requests.get(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers)
        
        if r.ok: 
            try: self.dataset = pd.read_csv(StringIO(r.text), sep=";")
            except: self.dataset = pd.DataFrame()
        else: raise Exception(f"Couldn't get data from existing chart. Response: {r.reason}")
        
    

        
        
        
    def disable_grid(self):
        
        # Set a few visualization properties that control the grid visibility on charts.
        self.metadata["metadata"]['visualize']["y-grid"] = "off"
        self.metadata["metadata"]['visualize']["x-grid"] = "off"
        
        self.metadata["metadata"]['visualize']["y-grid-lines"] = "off"
        self.metadata["metadata"]['visualize']["x-grid-lines"] = "off"
        
        # Send the metadata representation in this class to the datawrapper graphic.
        self.set_metadata()
        
        return self
        
        
        
        
        
    
    def data(self, data: pd.DataFrame):
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "text/csv",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }

        payload = data.to_csv(sep=";")
        
        r = requests.put(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers, data=payload.encode('utf-8'))

        if r.ok: logging.info(f"SUCCESS: Data added to chart.")
        else: raise DatawrapperAPIError(f"Chart data couldn't be added. Response: {r.reason}")
        
        self.set_metadata()
        
        return self
    




# This class defines methods and variables for Datawrapper locator maps.
# It is also extended by the hurricane map class below.
class Map(Graphic):
    
    # Script_name variable is used to pull the right icon templates from the assets folder, and is set on init.
    global script_name
    global icon_list
    
    def __init__(self,
                 *args,
                 **kwargs
                 ):
        super(Map, self).__init__(*args, **kwargs)
        
        self._check_graphic_type("locator-map")
        
        self.icon_list = dw_icons
        
        # This bit of code tries to load in data from the map in the DW app, but is not working currently.
        # markers = [self.get_markers()]
        
        # dfs = []
        
        # for marker in markers:
        #     df = pd.DataFrame({'id': [marker["id"]]})
            
        #     df["type"] = marker["type"]
                          
        #     for property in ["id", "title", "icon", "scale", "markerColor", "markerSymbol", "anchor", "visible"]:
        #         df[property] = marker[property] if hasattr(marker, property) else np.nan
            
        #     if marker["type"] == "point":
                
        #         df["tooltip"] = marker["tooltip"]["text"]
        #         df["latitude"] = marker["coordinates"][1]
        #         df["longitude"] = marker["coordinates"][0]
        #         df["icon"] = marker["icon"]["id"]
                
        #     else:
        #         try: df["geometry"] = shape(marker["feature"]["geometry"]).wkt
        #         except KeyError: df["geometry"] = shape(marker["features"]["feature"])
            
        #     dfs.append(df)
            
        # self.dataset = pd.concat(dfs)
     
     
     
     
    # Check markerColor to make sure it's a valid hex code.
    def _check_if_valid_hexcode(self, string):
        match = re.search("#[A-Za-z0-9]{6}", string)
        if match is None:
            return False
        else:
            return True
     
     
     
     
     
    
    def data(self,
             input_data: pd.DataFrame | geopandas.GeoDataFrame,
             append: str = None):
        
        """Uploads your data the map as markers.
        
        This method handles the majority of the heavy lifting for map data. In essence, it converts either a pd.DataFrame or a geopandas.GeoDataFrame to a GEOJson object, then replaces values in a template with custom values specified in the dataframe.
        
        Args:
            input_data (pd.DataFrame): The dataframe that you ultimately want to upload.

        Returns:
            object: Returns the datawrapper graphic object so methods can be chained.
        """
        
        # New list for storing the altered geojson.
        new_features = []
        
        # If the input data is a GeoDataFrame (rather than a pandas DataFrame), then change the CRS.
        if isinstance(input_data, geopandas.GeoDataFrame):
            input_data = input_data.to_crs("EPSG:4326")
        
        # Define a list of marker values that are allowed for various marker properties.
        ALLOWED_VALUES = {
            "marker": ["point", "area"],
            "anchor": ["middle-left", "middle-center", "middle-right", "bottom-left", "bottom-center", "bottom-right", "top-left", "top-center", "top-right"],
            "icon": [key for key, value in self.icon_list.items()]
        }
        
        # This loops through each row in the dataframe that was input and turns it into the properly formatted JSON object.
        for i, feature in input_data.iterrows():
            
            # Check if a marker type is specified. Throw an error if it's not provided.
            try: marker_type = feature["type"]
            
            # This bit of code checks a few things to define default marker types (points or areas).
            except: 
                # If there's a defined geometry property that's not a point, it's an area.
                if "geometry" in feature and not pd.isna(feature["geometry"]) and not isinstance(feature["geometry"], Point):
                    marker_type = "area"
                    
                # If there's a latitude column and a longitude value, OR if there's a Point feature provided, it's a point.
                elif ("latitude" in feature and "longitude" in feature and not pd.isna(feature["latitude"]) and not pd.isna(feature["longitude"])) or "geometry" in feature and isinstance(feature["geometry"], Point):
                    marker_type = "point"
                    
                    feature["longitude"] = float(feature["geometry"].x)
                    feature["latitude"] = float(feature["geometry"].y)
                # If none of these things, then the marker type cannot be inferred, and we raise an error.    
                else:
                    raise MissingDataError(f"Type of marker cannot be inferred from data provided. Please specify a marker type for all rows in your Dataframe.")
            
            # Check to make sure values that have an allowed list above are correctly entered, and throw an error if they're not.
            for marker_property, _list in ALLOWED_VALUES.items():
                if marker_property in feature and not pd.isna(feature[marker_property]) and feature[marker_property] not in _list:
                    raise InvalidMarkerDataError(marker_property, feature[marker_property], _list)
            
            for property in ["markerColor", "fill", "stroke", "markerTextColor"]:
                
                if property in feature and not pd.isna(feature[property]):
                    is_hexcode = self._check_if_valid_hexcode(str(feature[property]))
                    
                    if property in ["fill", "stroke"] and not is_hexcode and not isinstance(feature[property], bool):
                        raise InvalidHexcodeError()
                    elif property not in ["fill", "stroke"] and not is_hexcode:
                        raise InvalidHexcodeError()
        
            
            # Load the template feature object depending on the type of each marker (area or point). Throw an error if the file can't be found.
            if marker_type == "point":
                
                new_feature = {
                "type": "point",
                "title": feature["title"] if "title" in input_data and not pd.isna(feature["title"]) else "",
                "icon": self.icon_list[feature["icon"]] if "icon" in input_data and not pd.isna(feature["icon"]) else self.icon_list["circle"],
                "scale": feature["scale"] if "scale" in input_data and not pd.isna(feature["scale"]) else 1.1,
                "textPosition": True,
                "markerColor": feature["markerColor"] if "markerColor" in input_data and not pd.isna(feature["markerColor"]) else "#C42127",
                "markerSymbol": feature["markerSymbol"] if "markerSymbol" in input_data and not pd.isna(feature["markerSymbol"]) else "",
                "markerTextColor": "#333333",
                "anchor": feature["anchor"] if "anchor" in input_data and not pd.isna(feature["anchor"]) else "middle-left",
                "offsetY": 0,
                "offsetX": 0,
                "labelStyle": "plain",
                "text": {
                    "bold": False,
                    "color": "#333333",
                    "fontSize": 14,
                    "halo": "#f2f3f0",
                    "italic": False,
                    "space": False,
                    "uppercase": False
                },
                "class": "",
                "rotate": 0,
                "visible": feature["visible"] if "visible" in input_data and not pd.isna(feature["visible"]) else True,
                "locked": False,
                "preset": "-",
                "visibility": {
                    "desktop": feature["visible"] if "visible" in input_data and not pd.isna(feature["visible"]) else True,
                    "mobile": feature["visible"] if "visible" in input_data and not pd.isna(feature["visible"]) else True,
                },
                "tooltip": {
                    "text": feature["tooltip"] if "tooltip" in input_data and not pd.isna(feature["tooltip"]) else ""
                },
                "connectorLine": {
                    "enabled": False,
                    "arrowHead": "lines",
                    "type": "curveRight",
                    "targetPadding": 3,
                    "stroke": 1,
                    "lineLength": 0
                },
                }

                # For coordinates for point markers, users can specify either points in WKY Point form,
                # or latitude and longitude columns. This logic handles the creation of the coordinates
                # list differently depending on which columns are present.
                if "longitude" and "latitude" in feature:
                    new_feature["coordinates"] = [feature["longitude"], feature["latitude"]]
                elif hasattr(feature, "geometry"):
                    try: new_feature["coordinates"] = [float(feature["geometry"].x), float(feature["geometry"].y)]
                    except: raise GeometryError(f"There was an issue with converting geometry column coordinates into coordinates. Please ensure geometry for point markers is a WKT of type Point.")
                else:
                    raise MissingDataError(f'No geometry or latitude and longitude columns found in input data.')
            
            
            
            elif marker_type == "area":
                    
                new_feature = {
                    "type": "area",
                    "title": feature["title"] if "title" in input_data and not pd.isna(feature["title"]) else "",
                    "visible": feature["visible"] if "visible" in input_data and not pd.isna(feature["visible"]) else True,
                    "fill": feature["fill"] if "fill" in input_data and not pd.isna(feature["fill"])and isinstance(feature["fill"], bool) else True,
                    "stroke": feature["stroke"] if "stroke" in input_data and not pd.isna(feature["stroke"]) and isinstance(feature["stroke"], bool) else True,
                    "exactShape": False,
                    "highlight": False,
                    "markerColor": feature["markerColor"] if "markerColor" in input_data and not pd.isna(feature["markerColor"]) else "#C42127",
                    "properties": {
                        "fill": feature["fill"] if "fill" in input_data and not pd.isna(feature["fill"]) and isinstance(feature["fill"], str) else "#C42127",
                        "fill-opacity": feature["fill-opacity"] if ("fill-opacity" in feature and feature["fill-opacity"] and not pd.isna(feature["fill-opacity"])) else 0.3,
                        "stroke": feature["stroke"] if "stroke" in input_data and not pd.isna(feature["stroke"]) and isinstance(feature["stroke"], str) else "#000000",
                        "stroke-width": feature["stroke-width"] if ("stroke-width" in feature and feature["stroke-width"] and not pd.isna(feature["stroke-width"])) else 1,
                        "stroke-opacity": feature["stroke-opacity"] if ("stroke-opacity" in feature and feature["stroke-opacity"] and not pd.isna(feature["stroke-opacity"])) else 0.7,
                        "stroke-dasharray": feature["stroke-dasharray"] if "stroke-dasharray" in input_data and not pd.isna(feature["stroke-dasharray"]) else "100000",
                        "pattern": "solid",
                        "pattern-line-width": 2,
                        "pattern-line-gap": 2
                    },
                    "icon": {"id": "area",
                        "path": "M225-132a33 33 0 0 0-10 1 38 38 0 0 0-27 28l-187 798a39 39 0 0 0 9 34 37 37 0 0 0 33 12l691-93 205 145a38 38 0 0 0 40 2 38 38 0 0 0 20-36l-54-653a38 38 0 0 0-17-28 38 38 0 0 0-32-5l-369 108-274-301a39 39 0 0 0-28-12z",
                        "horiz-adv-x": 1000,
                        "scale": 1.1,
                        "outline": "2px"},
                    "visibility": {
                        "desktop": feature["visible"] if "visible" in input_data and not pd.isna(feature["visible"]) else True,
                        "mobile": feature["visible"] if "visible" in input_data and not pd.isna(feature["visible"]) else True,
                    },
                    "feature": {
                        "type": "Feature",
                        "properties": {},
                        "geometry": Feature(geometry=feature["geometry"], properties={})["geometry"]
                        }
                }
            
            
            
            new_features.append(new_feature)

        
        # If there are other shapes to be added (ie. highlights of provinces, etc.) then this will use a naming convention to grab them from the shapes folder.
        # Check if there are any extra shapes to add.
        
        if append:
            
            # Open the shape file.
            with open(append, 'r') as f:
                extra_shapes = json.load(f)
                
                # If there is only one object and it's not in a list, make it a list.
                if type(extra_shapes) != list:
                    extra_shapes = [extra_shapes]
                    
                # Iterate through the list and add it to our markers list.
                for shape in extra_shapes:
                    new_features.append(shape)
        
        # Datawrapper uses a convention to ID features following m0, m1, m2 etc. Add these in once we have all the markers in a list so there are no duplicates.
        for i, feature in enumerate(new_features):
            feature["id"] = "m" + str(i)
        
        # Change layout of the markers to match what Datawrapper likes to receive.    
        payload = {"markers": new_features}
        payload = json.dumps(payload)
        
        # Make the HTTP request to the Datawrapper API to upload the data.
        headers = {"Authorization": f"Bearer {self.DW_AUTH_TOKEN}"}
        r = requests.put(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers, data=payload)

        if r.ok: logging.info(f"SUCCESS: Data added to chart.")
        else: raise Exception(f"ERROR: Chart data couldn't be added. Response: {r.reason}")
        
        
        return self
    
    
    
    
    
    
    
    
    
    # This method is mostly used for testing and debugging. It can be called to save the data that was just uploaded to a chart
    # so it can be easily inspected.
    def get_markers(self, save: bool = False):
        
        headers = {
            "Accept": "text/csv",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
            }
        
        response = requests.get(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers)
        markers = response.json()["markers"]
        
        if save:
            with open(f"{self.path}/markers-{self.script_name}.json", 'w') as f:
                json.dump(markers, f)
                
        return markers
    
    



# The StormMap class is a special extension of the Map class that takes data from the NOAA and turns
# it into a hurricane map with standard formatting. It takes one input: the storm ID of the hurricane
# or tropical storm that can be taken from the NOAA's National Hurricane Center.

# The NOAA stores this data in at least two separate zipfiles that need to be pulled in and processed.
class StormMap(Map):
    
    """A special maps class for loading in NOAA hurricane center data into a locator map.
    
    This class is implemented by passing both an XML url and a storm ID into the constructor.
    
    Args:
        storm_id (str): The ID of the storm that you want to track.
        active (bool): Whether or not the storm is still active.
        chart_id (str): The ID of the chart you're bringing into the module. Providing this string value is the typical implementation of this library.
        copy_id (str, optional): Instead of a chart_id, you can specify the id of a chart to copy. Keep in mind that this will keep making copies if you keep running code, so it's best run only once, then use chart_id.
        auth_token (str, optional): The auth_token from Datawrapper. You can authenticate by passing this into the class instantiation, or by putting an auth.txt file in your project's root folder with the token.
        folder_id (str, optional): If a new chart is being created because no chart_id or copy_id is passed, this is where you specify which folder to create it in.

    Attributes:
        storm_id (str): The ID of the storm in the map.
        windspeed (str): The current windspeed.
        storm_name (str): The name of the tracked storm.
        storm_type (str): Is the storm currently remnants, a tropical depression, or a hurricane?
        
    Returns:
        object: Returns self, the instance of the Graphic class. Can be chained with other methods.
    """
    
    # Some variables that we want to be able to access when the class is instantiated.
    global storm_id
    global windspeed
    global storm_name
    global storm_type
    global active
    
    
    # TODO allow passing of just storm_id to track the storm, rather than XML_id as well.
    def __init__(self, storm_id: str, chart_id: str = None, copy_id: str = None):
        
        # Set storm id from the input given to the class constructor.
        if isinstance(storm_id, str):
            self.storm_id = [storm_id]
        else:
            self.storm_id = storm_id
        
        super().__init__(chart_id, copy_id)
    
    
    
    # This method gets the shapefile from the NOAA, which is in a zipfile.
    def __get_shapefile(self, filename, layer):
        filename = filename.lower()
        
        # Download and open the zipfile.
        try: resp = urlopen(filename)
        except urllib.error.HTTPError: raise Exception(f"Resource is forbidden. It's likely the shapefile for probable path is not publicly accessible.")
        
        # List out names of files in the zipfile.
        files = ZipFile(BytesIO(resp.read())).namelist()
        
        # Put it into a dataframe for easy iteration.
        files = pd.Series(files)

        file_name = files[files.str.contains(layer)].to_list()[0].replace(".shp", "")
        
        # Returns a geopandas df.
        return geopandas.read_file(filename, layer=file_name)
    
    
    
    
    # This function gets the total path of the hurricane, which is stored in a separate zip file entirely from the others.
    # This function is not used currently.
    def __total_path(self, storm_id):
        
        # Get the best track zipfile that contains the shapefile about the historical path of the storm.
        best_track_zip = f"https://www.nhc.noaa.gov/gis/best_track/{storm_id}_best_track.zip"
        
        # Pull the points shapefile out of this zip file.
        points = self.__get_shapefile(best_track_zip, "pts.shp$")

        # points = points[points["STORMNAME"] == self.storm_name.upper()]
        points = points.rename(columns={"LAT": "latitude", "LON": "longitude"})

        # Turn the geometry column into a lat/long column.
        # We do this because that's what Graphics's data() method uses for points (it does not recognize WKT POINT() features).
        points["longitude"] = points["geometry"].x.astype(float)
        points["latitude"] = points["geometry"].y.astype(float)
        points = points.drop(columns=["geometry"])
        
        # Set some attributes that are required by the data() method for points that will eventually be called on this dataset.
        points["type"] = "point"
        points["icon"] = "circle"
        points["scale"] = 1.1
        
        points["markerSymbol"] = points["STORMTYPE"].str.replace("M", "H")
        points.loc[~points["markerSymbol"].isin(["D", "S", "H"]), "markerSymbol"] = ""
        points["markerColor"] = points["markerSymbol"].replace({"H": "#e06618"})
        points.loc[points["markerColor"] != "H", "markerColor"] = "#567282"
        
        # Pull the line shapefile out of this zip file.
        # This is what makes the "historical path" dotted line on the Datawrapper chart.
        line = self.__get_shapefile(best_track_zip, "lin.shp$")
        
        # Set some attributes that are required by the data() method for areas that will eventually be called on this dataset.
        line["stroke"] = "#000000"
        line["type"] = "area"
        line["stroke-dasharray"] = "1,2.2"
        line["fill-opacity"] = 0.0
        
        # line = line[line["SS"] >= 1]
        
        line = line.dissolve(by='STORMNUM')
        
        df = pd.concat([line])
        
        # This bit of code standardizes the storm classifcations into a style that Datawrapper can use (single letters, not two).
        # df["STORMTYPE"] = (df["STORMTYPE"]
        #                     .replace({"TS": "S", "HU": "H", "TD": "D"})
        #                     .loc[df["STORMTYPE"].isin(["D", "H", "S"]), :]
        #                     )
        
        return df
    
    # This method is a custom version of Map's data() method, which is then called after calling this.
    def data(self):
            
        markers_list = []
        
        for storm_id in self.storm_id:
            # Get storm metadata.
            folder = storm_id[:-4].upper()
            
            # There are some issues with the folders of NOAA following naming conventions. This should fix it.
            if folder[:2] == "AL":
                folder = folder.replace("AL", "AT")
            
            filename = f"https://www.nhc.noaa.gov/storm_graphics/{folder}/atcf-{storm_id.lower()}.xml"
            
            try: metadata = pd.read_xml(filename, xpath="/cycloneMessage")
            except urllib.error.HTTPError: raise NoStormDataError()
            
            metadata.columns = metadata.columns.str.strip()
            # Split the marker for the center of the storm into latitude and longitude values.
            metadata = metadata.rename(columns={"centerLocLongitude": "longitude",
                                        "centerLocLatitude": "latitude",
                                        "systemSpeedKph": "windspeed",
                                        "systemName": "name",
                                        "systemType": "type"
                                        })
            
            # Save windspeed in object variables.
            self.windspeed = metadata.at[0, "windspeed"]
            
            # Save name of storm in object variables.
            self.storm_name = metadata.at[0, "name"].capitalize()
            
            # Save type of storm in object variables.
            self.storm_type = metadata.at[0, "type"]
            
            if self.storm_type == "REMNANTS OF":
                self.active = False
            else:
                self.active = True
            
            
            # Pull in data from NOAA five day forecast shapefile.
            # This is where we get the centre line, probable path cone shape, and points in probable path.
            five_day_latest_filename = f"https://www.nhc.noaa.gov/gis/forecast/archive/{storm_id}_5day_latest.zip"
            
            # Get points layer from five day forecast shapefile.
            points = self.__get_shapefile(five_day_latest_filename, "5day_pts.shp$")
            
            # Start by processing the points shapefile
            points["longitude"] = points["geometry"].x.astype(float)
            points["latitude"] = points["geometry"].y.astype(float)
            points = points.drop(columns=["geometry"])
            
            # Define necessary info for point markers.
            points["type"] = "point"
            
            # String together a title from information in each row.
            points['DATELBL'] = pd.to_datetime(points['DATELBL'])
            # points["title"] = points['DATELBL'].dt.strftime("%A") + "<br>" + points['DATELBL'].dt.strftime("%I:%M %p").replace("<br>0", "<br>")
            
            # Marker symbols are the little letters in each point marker.
            points["markerSymbol"] = points["DVLBL"]
            
            # Define colors based on the letters we use to mark each point.
            points["markerColor"] = points["markerSymbol"].replace({"D": "#567282", "S": "#567282", "H": "#e06618"})
            
            # Define label anchors.
            points["anchor"] = "middle-left"
            
            # Define a written out version of what kind of storm it is at each point for use in the tooltip.
            points.loc[points["DVLBL"] == "D", "storm_type"] = "Depression"
            points.loc[points["DVLBL"] == "H", "storm_type"] = "Hurricane"
            points.loc[points["DVLBL"] == "S", "storm_type"] = "Storm"
            
            # This checks os, and returns a leading character to remove 0 from strftime.
            # On windows, you have to use #. On Linux and Mac, it's a hyphen.
            if self._os_name == "nt":
                leading_char = "#"
            else:
                leading_char = "-"
            
            # Put together the tooltip for each map point.
            points["tooltip"] = "On " + points['DATELBL'].dt.strftime("%b %e") + " at " + points['DATELBL'].dt.strftime("%" + leading_char + "I:%M %p").str.replace(" 0", "", regex=True) + " EST, the storm is projected to be classified as a " + points["storm_type"].str.lower() + "."
            
            # Get center line layer from five day forecast shapefile.
            centre_line = self.__get_shapefile(five_day_latest_filename, "5day_lin.shp$")
            
            # Define properties unique to centre line.
            
            centre_line["stroke"] = "#000000"
            centre_line["stroke-width"] = 2.0
            centre_line["fill"] = False
            centre_line["title"] = "Probable path centre line"
            
            # Get probable path layer from five day forecast shapefile.
            # This layer is the cone that shows where the storm may move next.
            probable_path = self.__get_shapefile(five_day_latest_filename, "5day_pgn.shp$")
            
            # Define properties unique to probable path shape.
            probable_path["fill"] = "#6a3d99"
            probable_path["stroke"] = False
            probable_path["fill-opacity"] = 0.3
            probable_path["title"] = "Probable path"
            
            # Call the method that returns our total path information. This holds historical info about where the hurricane has been.
            # TODO add point information back into historical path?
            # total_path = self.__total_path(storm_id=self.storm_id)
            
            # Get the best track zipfile that contains the shapefile about the historical path of the storm.
            best_track_zip = f"https://www.nhc.noaa.gov/gis/best_track/{storm_id}_best_track.zip"
            historical_path = self.__get_shapefile(best_track_zip, "lin.shp$")
            
            # Set some attributes that are required by the data() method for areas that will eventually be called on this dataset.
            historical_path["stroke"] = "#000000"
            historical_path["stroke-dasharray"] = "3,2.2"
            historical_path["stroke-width"] = 2.0
            historical_path["fill"] = False
            
            # Dissolve several features of this line into one long line, as the individual segments are not of interest to us.
            historical_path = historical_path.dissolve(by='STORMNUM')
            
            # Concatenate all our area markers together so we can define some common characteristics.
            shapes = pd.concat([centre_line, probable_path, historical_path])
            
            # Define some common style points for the centre line and the probable path.
            shapes["icon"] = "area"
            shapes["type"] = "area"
            
            # Concatenate areas and points into one large dataframe so we can upload it.
            markers = pd.concat([shapes, points])
            
            markers_list.append(markers)

        all_markers = pd.concat(markers_list)
        # Save as the object's dataset.
        self.dataset = all_markers
        
        # Pass the dataset we've just prepped into the super's data method.
        return super(self.__class__, self).data(self.dataset)
    
    
class FibonacciChart(Chart):
    
    """A custom chart type that creates a fibonacci spiral with your data.
    
    Args:
        chart_id (str): The ID of the chart you're bringing into the module. Providing this string value is the typical implementation of this library.
        copy_id (str, optional): Instead of a chart_id, you can specify the id of a chart to copy. Keep in mind that this will keep making copies if you keep running code, so it's best run only once, then use chart_id.
        auth_token (str, optional): The auth_token from Datawrapper. You can authenticate by passing this into the class instantiation, or by putting an auth.txt file in your project's root folder with the token.
        folder_id (str, optional): If a new chart is being created because no chart_id or copy_id is passed, this is where you specify which folder to create it in.

    Attributes:
        CHART_ID (str): The CHART_ID is a unique ID that can be taken from the URL of datawrappers. It's required to use the DW api.
        metadata (str): Holds the chart's metadata when the graphic is instantiated.
        dataset (pd.DataFrame): Represents the data that is uploaded or will be uploaded to the graphic.
        DW_AUTH_TOKEN (str): Token to authenticate to Datawrapper's API.
        path (str): Path that the script is running from using this module.
        script_name (str): Name of the script currently running using this module.
        
    Returns:
        object: Returns self, the instance of the Graphic class. Can be chained with other methods.
    """
    
    def __init__(self, chart_id: str = None, copy_id: str = None, folder_id: str = None):
        
        super().__init__(chart_id, copy_id, folder_id)
        
        
    def data(self, input_data: pd.DataFrame):
        
        """Uploads your data and applies fibonacci coordinates to each point.
        
        Args:
            input_data (pd.DataFrame): The dataframe that you ultimately want to plat on a fibonacci chart.

        Returns:
            object: Returns the datawrapper graphic object so methods can be chained.
        """
        
        # Get the number of rows in the input dataframe.
        num_points = len(input_data)
        
        # Math to get fibonacci coordinates based on the number of records in the input data.
        ga = np.pi * (3 - np.sqrt(5))
        theta = np.arange(num_points) * ga

        radius = np.sqrt(np.arange(num_points) / float(num_points))
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        
        # Add two new columns to our the input dataframe which can be used to plot on a Datawrapper scatterplot.
        input_data["x"] = x
        input_data["y"] = y
        
        # Update the dataset property of this object.
        self.dataset = input_data
        
        # Turn off the grid.
        self.disable_grid()
        
        # Pass the new dataframe with the two new columns into Chart's data method to finish things off.
        return super(self.__class__, self).data(self.dataset)
    
    
    
    
    
    
    
    
class CircleChart(Chart):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
        
    def data(self, input_data: pd.DataFrame):
        
        # One point will be plotted for each row. It's advisable to keep your dataset small.
        # For calendar plots, you should have one row for each month.
        # The circle will start at the top, and plot clockwise.
        segments = len(input_data)
        
        R = 1
        max_theta = 2* np.pi
        
        circle_start = (0.25*max_theta) + (max_theta/segments)
        circle_end = (max_theta+(0.25*max_theta)) + (max_theta/segments)
        
        list_t = list(np.arange(circle_start, circle_end, max_theta/segments))[::-1]
        x = [(R*math.cos(x_y)) for x_y in list_t]
        y = [(R*math.sin(x_y)) for x_y in list_t]

        input_data["x"] = x
        input_data["y"] = y
        
        # Update the dataset property of this object.
        self.dataset = input_data
        
        # Turn off the grid.
        self.disable_grid()
        
        # Pass the new dataframe with the two new columns into Chart's data method to finish things off.
        return super(self.__class__, self).data(self.dataset)
    
    



class CalendarChart(Chart):
    
    
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        

    
    def data(self, input_data: pd.DataFrame, date_col: str, timeframe: str = "month"):
        
        # Convert the specified date column into pd.datetime.
        try: input_data[date_col] = pd.to_datetime(input_data[date_col])
        except: raise Exception(f"There was a problem converting your provided column to a pandas datetime series.")
        
        
        # This will output a calendar plot with a month scale (ie. days of the week are lined up.)
        if timeframe == "month":
            
            # Get the numerical day of week for each date in the dataframe.
            # This will make up the X coordinates (left to right on the graphic)
            input_data["x"] = input_data[date_col].dt.dayofweek
            
            # Make an empty series for the y column.
            input_data["y"] = pd.NA
        
            # Set all 0s (ie. every Monday) to a new week number (1, 2, 3 etc.)
            input_data.loc[input_data["x"] == 0, "y"] = range(2,(len(input_data.loc[input_data["x"] == 0, "y"])+2))
            
            # Forward fill for the other weekday values (1-6).
            # This makes up our y axis.
            # the .fillna after the ffill here is necessary, because the first few days don't get any numbers otherwise.
            input_data["y"] = input_data["y"].fillna(method="ffill").fillna(1)
        
        
        # This will output a calendar on a year scale, rather than a month scale.
        if timeframe == "year":
            
            density = 15
            
            input_data["x"] = input_data[date_col].dt.dayofyear
            
            # Make an empty series for the y column.
            input_data["y"] = pd.NA
        
            # # Set all 0s (ie. every Monday) to a new week number (1, 2, 3 etc.)
            # input_data.loc[input_data["x"]%12 == 0, "y"] = range(2,(len(input_data.loc[input_data["x"]%12 == 0, "y"])+2))
            
            input_data["y"] = input_data["x"].apply(lambda x: math.floor(x/density))
            input_data["x"] = input_data["x"] - density*(input_data["y"])
            
            # Forward fill for the other weekday values (1-6).
            # This makes up our y axis.
            # the .fillna after the ffill here is necessary, because the first few days don't get any numbers otherwise.
            input_data["y"] = input_data["y"].fillna(method="ffill").fillna(1)
        
        # Add a column with the English name for each weekday and each month.
        input_data["day_of_week"] = input_data[date_col].dt.strftime("%A")
        input_data["month"] = input_data[date_col].dt.strftime("%B")
        
        # Update the dataset property of this object.
        self.dataset = input_data
        
        # Set a few visualization properties that are key to showing this data properly.
        self.metadata["metadata"]['visualize']['y-axis']["range"] = [input_data["y"].max()+0.5, input_data["y"].min()-0.5]
        
        # Turn off the grid.
        self.disable_grid()
        
        # Send the metadata representation in this class to the datawrapper graphic.
        self.set_metadata()
        
        # Pass the new dataframe with the two new columns into Chart's data method to finish things off.
        return super(self.__class__, self).data(self.dataset)