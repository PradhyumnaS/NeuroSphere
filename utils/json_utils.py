import json
from datetime import datetime
import pandas as pd

class TimestampEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles pandas Timestamp and datetime objects"""
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        return super().default(obj)

def serialize_to_json(data):
    """
    Serialize data to JSON, handling timestamp objects properly
    
    Args:
        data: The data to serialize
        
    Returns:
        str: JSON string
    """
    return json.dumps(data, cls=TimestampEncoder)

def save_to_json_file(data, file_path):
    """
    Save data to a JSON file, handling timestamp objects properly
    
    Args:
        data: The data to save
        file_path: Path to save the JSON file
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, cls=TimestampEncoder)
