import requests
import json
import os
import sys
import pandas as pd
import geopandas
from typing import Union
from datawrappergraphics.icons import dw_icons
from datawrappergraphics.DatawrapperGraphic import DatawrapperGraphic

# This class defines methods and variables for Datawrapper locator maps.
# It is also extended by the hurricane map class below.
class Map(DatawrapperGraphic):
    
    # Script_name variable is used to pull the right icon templates from the assets folder, and is set on init.
    global script_name
    global icon_list
    
    
    
    def __init__(self, chart_id: str = None, copy_id: str = None):
        super().__init__(chart_id, copy_id)
        
        self.script_name = os.path.basename(sys.argv[0]).replace(".py", "").replace("script-", "")
        
        self.icon_list = dw_icons
        
     

     
     
    ## This function converts a pandas dataframe into geojson if the data you're using doesn't import correctly into Geopandas.
    def df_to_geojson(self, dframe: pd.DataFrame, lat: str = 'latitude', lon: str = 'longitude'):
        
        # create a new python dict to contain our geojson data, using geojson format
        geojson = {'type':'FeatureCollection', 'features':[]}

        # loop through each row in the dataframe and convert each row to geojson format
        for _, row in dframe.iterrows():
            
            # create a feature template to fill in
            feature = {'type':'Feature',
                    'properties':{},
                    'geometry':{'type':'Point',
                                'coordinates':[]}}

            # fill in the coordinates
            feature['geometry']['coordinates'] = [row[lon],row[lat]]

            # for each column, get the value and add it as a new feature property
            for prop in dframe.columns:
                feature['properties'][prop] = row[prop]
            
            # add this feature (aka, converted dataframe row) to the list of features inside our dict
            geojson['features'].append(feature)
        
        return geojson
     
     
     

        
     
     
     
     
    # This method handles the majority of the heavy lifting for map data.
    # In essence, it converts either a pd.DataFrame or a geopandas.GeoDataFrame to a GEOJson object, then
    # replaces values in a template with custom values specified in the dataframe.
    def data(self, input_data: Union[pd.DataFrame, geopandas.GeoDataFrame]):
        
        # Define a list of marker types that are allowed.
        allowed_marker_type_list = ["point", "area"]
        
        # Define a list of icon types that are allowed
        # TODO write code to pull this list programmatically when a new template is added to assets folder.
        allowed_icon_list = ["fire", "attention", "circle-sm", "circle", "city", "droplet", "fire", "star-2", "area"]
        
        # Create an id column that uses Datawrapper's ID naming convention.
        input_data.loc[:, 'id'] = range(0, len(input_data))
        input_data.loc[:, "id"] = input_data.loc[:, 'id'].apply(lambda x: f"m{x}")
        
        # Check if the data input is a pandas dataframe or a geopandas dataframe. if it's pandas, call df_to_geojson(). If not, convert crs and convert geopandas to json.
        # The outcome of this if/else is a list of json objects that can be iterated through.
        if not isinstance(input_data, geopandas.GeoDataFrame):
            input_data = self.df_to_geojson(input_data)
        else:
            input_data = input_data.to_crs("EPSG:4326")
            input_data = json.loads(input_data.to_json())
        
        # Get only the features from the object.
        features = input_data["features"]
        
        # New list for storing the altered geojson.
        new_features = []
        
        for feature in features:
            
            # Check properties that are required to be able to run this function and raise an error if they are not provided.
            
            try: icon = feature["properties"]['icon']
            except KeyError: raise Exception(f"Icon was not specified in your file. Please add a column for this property.")
            
            # Check to make sure the icon type we specified is in the list of allowed marker types.
            if icon not in allowed_icon_list:
                raise Exception(f"It looks like you haven't provided a valid icon type. Please ensure the value is one of: {', '.join(allowed_icon_list)}.")
            
            try: marker_type = feature["properties"]["type"]
            except KeyError: raise Exception(f"Marker type was not specified in your file. Please add a column for this property.")
            
            # Check to make sure the marker type we specified is in the list of allowed marker types.
            if marker_type not in allowed_marker_type_list:
                raise Exception(f"It looks like you haven't provided a valid marker type. Please ensure the value is one of: {', '.join(allowed_marker_type_list)}.")
            
            # Load the template feature object depending on the type of each marker (area or point). Throw an error if the file can't be found.
            with open(f"assets/{marker_type}.json", 'r') as f:
                template = json.load(f)
            
            # These properties have to be handled a little differently than just loop through and replace the values in the template with the new values provided.
            exclusion_list = ["tooltip", "icon", "geometry", "fill", "stroke", "visibility"]

            # This code loops through every value provided and replaces that value in the template we loaded above. If the value is not a str or an int, it won't include it.
            new_feature = {k: feature["properties"][k] if (k in feature["properties"] and k not in exclusion_list and isinstance(v, Union[int, str])) else v for k, v in template.items()}
            
            # Now we handle some of the outliers specified in the exclusion list.
            # Tooltip has to be embedded in an object.
            try: new_feature["tooltip"] = {"text": feature["properties"]["tooltip"]}
            except: new_feature["tooltip"] = {"text": template["tooltip"]}
            
            # This pulls the "visibility" values from whatever is specified for "visible". This means that currently, you can not disable
            # anything from showing on mobile and desktop seperately.
            # TODO implement separate control for visiblity on desktop and mobile. If values are not specified, use default values from template.
            try: new_feature["visibility"] = {
                    "desktop": feature["properties"]["visible"],
                    "mobile": feature["properties"]["visible"],
                }
            except KeyError: new_feature["visibility"] = {
                    "desktop": template["visible"],
                    "mobile": template["visible"],
                }
            
            
            # Some properties are different if our entry is a point rather than an area.
            # Here we handle the points.
            if marker_type == "point":
                
                # Coordinates are provided for points by a latitude and a longitude column. They must be specified or an exception is thrown.
                try: new_feature["coordinates"] = feature["geometry"]["coordinates"]
                except TypeError:
                    # Latitude and longtitude are required inputs, so throw an error if they can't be found.
                    try: new_feature["coordinates"] = [float(feature["properties"]["longitude"]), float(feature["properties"]["latitude"])]
                    except KeyError: raise Exception(f"Latitude or longitude has not been provided. Please provide those values.")
                
                # Icon is an object and the whole object needs to be taken from the template file. A string is what's provided by the dataframe, so we have to do this specially.
                try: new_feature["icon"] = self.icon_list[feature["properties"]["icon"]]
                except: raise Exception(f"Icon template not found. Please specify a valid icon.")
            
            # Here we handle the special properties of area markers.        
            elif marker_type == "area":
                
                # Area markers have a special attribute called "feature" that houses the geometry. Note the "type" must be feature or DW will error.
                new_feature["feature"] = {
                    "type": "Feature",
                    "properties": [],
                    "geometry": feature["geometry"]
                    }
                
                # The "stroke" needs to be handled differently because the stroke attribute in the datawrapper object is
                # a boolean value that controls if the stroke is visible or not, whereas the dataframe specifies the stroke
                # color, not whether it's visible or not.
                # TODO allow for specification of stroke and fill to be enabled/disabled using boolean.
                try: new_feature["properties"]["stroke"] = feature["properties"]["stroke"]
                except: new_feature["properties"]["stroke"] = template["stroke"]
            
            # If marker type is not either point or area, throw an error. This differs from above error handling in that it
            # the above does not validate that icon is ponit or area.
            else: raise Exception(f"Something is wrong with your marker type.")
            
            new_features.append(new_feature)

        
        # If there are other shapes to be added (ie. highlights of provinces, etc.) then this will use a naming convention to grab them from the shapes folder.
        # Check if there are any extra shapes to add.
        if os.path.exists(f"assets/shapes/shapes-{self.script_name}.json"):
            
            # Open the shape file.
            with open(f"assets/shapes/shapes-{self.script_name}.json", 'r') as f:
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
        headers = {"Authorization": f"Bearer {self.auth()}"}
        r = requests.put(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers, data=payload)

        if r.ok: print(f"SUCCESS: Data added to chart.")
        else: raise Exception(f"ERROR: Chart data couldn't be added. Response: {r.reason}")
        
        return self
    
    
    
    
    
    
    
    
    
    # This method is mostly used for testing and debugging. It can be called to save the data that was just uploaded to a chart
    # so it can be easily inspected.
    def get_markers(self, save: bool = False):
        
        headers = {
            "Accept": "text/csv",
            "Authorization": f"Bearer {self.auth()}"
            }
        
        print(self.CHART_ID)
        response = requests.get(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers)
        markers = response.json()["markers"]
        
        if save:
            with open(f"markers-{self.script_name}.json", 'w') as f:
                json.dump(markers, f)
                
        return markers
    
    

