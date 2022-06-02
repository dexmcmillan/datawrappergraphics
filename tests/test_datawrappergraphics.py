import pandas as pd
from datawrappergraphics.Map import Map

def test_map():
    
    TEST_CHART_ID = "UPTcO"
    
    raw = pd.DataFrame({"title": ["Point 1"], "latitude": [50.2373819], "longitude": [-90.708556], "anchor": ["middle-right"], "tooltip": ["A test tooltip."], "icon": ["attention"]})
    
    assert (Map(chart_id=TEST_CHART_ID, auth_token="HQd4kFqSSQyh5I7dK7YKNonyG74UpldKls1KOShOWxZNbpZyrbgO1kNArRAfwW3I")
        .data(raw)
        .head(f"Testing datawrappergraphics library")
        .deck("")
        .publish()
    )