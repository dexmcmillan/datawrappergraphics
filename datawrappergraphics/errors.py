# Custom errors are defined here.

# This errors helps to control the kinds of values that are input into datawrapper (for example, the 'anchor' property can be one of only
# a handful of values, or your map will error out and not display anything.
class InvalidMarkerDataError(Exception):
    
    def __init__(self, field: str, input_value: str | int | float | bool, allowed_values_list: list):
        
        message = f"It looks like the {field} you provided ({input_value}) is not valid.\nPlease ensure the value is one of: {', '.join(allowed_values_list)}."
        
        super().__init__(message)
        
        
        
class InvalidHexcodeError(Exception):
    
    def __init__(self):
        
        super().__init__(f"The color you provided for one of your rows is not a valid 6-digit hexcode.")



class InvalidExportTypeError(Exception):
    
    def __init__(self, allowed_values_list: list):
        
        super().__init__(f"The file format you specified is invalid. Please select one of:  {', '.join(allowed_values_list)}.")
        
        
        
class NoStormDataError(Exception):
    
    def __init__(self):
        
        super().__init__(f"Invalid storm ID. Check that you've entered it correctly.")
        
        
        
class WrongGraphicTypeError(Exception):
        
    def __init__(self, type_input: str):
        
        super().__init__(f"The chart ID you've passed is a {type_input}. Please use the correct class (Map, Chart etc.) to load your graphic.")
        
        
class MissingDataError(Exception):
        
    def __init__(self, msg: str):
        
        super().__init__(msg)
        
        
class GeometryError(Exception):
        
    def __init__(self, msg: str = None):
        
        if msg != None:
            msg = f"There was a problem with your geometry. Please check that you've provided a latitude and longitude or geometry column."
        
        super().__init__(msg)
        
        
class DatawrapperAPIError(Exception):
        
    def __init__(self, msg: str = None):
        
        super().__init__(msg)