import requests
import os
import sys
import pandas as pd
from datawrappergraphics.DatawrapperGraphic import DatawrapperGraphic

# The Chart class defines methods and variables for uploading data to datawrapper charts (scatter plots, tables etc).
# Use this class to create a new, copy, or to manage a currently existing Datawrapper chart (ie. not a map!).
class Chart(DatawrapperGraphic):
    
    script_name = os.path.basename(sys.argv[0]).replace(".py", "").replace("script-", "")
    
    def __init__(self, chart_id: str = None, copy_id: str = None):
        super().__init__(chart_id, copy_id)
    
    def data(self, data: pd.DataFrame):
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "text/csv",
            "Authorization": f"Bearer {self.DW_AUTH_TOKEN}"
        }

        payload = data.to_csv()
        
        r = requests.put(f"https://api.datawrapper.de/v3/charts/{self.CHART_ID}/data", headers=headers, data=payload)

        if r.ok: print(f"SUCCESS: Data added to chart.")
        else: raise Exception(f"Chart data couldn't be added. Response: {r.reason}")
        
        return self
    
    