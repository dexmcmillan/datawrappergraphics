# Custom errors are defined here.

# This errors helps to control the kinds of values that are input into datawrapper (for example, the 'anchor' property can be one of only
# a handful of values, or your map will error out and not display anything.
class InvalidMarkerDataError(Exception):
    
    def __init__(self,
                 field: str,
                 input_value: str|int|float|bool,
                 allowed_values_list: list
                 ):
        
        message = f"It looks like the {field} you provided ({input_value}) is not valid.\nPlease ensure the value is one of: {', '.join(allowed_values_list)}."
        
        super().__init__(message)
        
        
        
class InvalidHexcodeError(Exception):
    
    def __init__(self):
        
        super().__init__(f"The color you provided for one of your rows is not a valid 6-digit hexcode.")