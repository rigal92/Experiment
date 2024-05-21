import json 
import pickle
from expy import Experiment, Event

def open_pickle(filename):
    """
    Read the Experiment from a binary file. 
    --------------------------
    DEPRECATED
    Replace with saving and reading using json. More stable and human
    readable. 
    Use for experiments saved using experiment v1.0.0
    --------------------------
    """
    with open(filename,"rb") as f:
        return pickle.load(f)

def read(filename):
    """
    Read the Experiment from a json file. 
    """
    ex = Experiment()
    with open(filename) as f:
        d = json.load(f)
    for key,value in d.items():
        ex[key] = read_event(value, flag = "read_json_file")
    ex.tidy_functions()
    return ex

def read_event(dic, flag = None):
    """
    Parse keywords from a dictionary and creates an event.

    Input
    --------------------------
    dic: dict
        dictionary to parse the event. 
        Accepted keys for the dictionary are: 
            "name", "attributes", "data", "function" 

    flag: str or None, default = None
        Argument passed to Event constructor. Handles special cases.
        Accepted values:
        - "read_json_file": handles the creation of the DataFrames 
          stored in the json experiment file 
    Returns
    --------------------------
    Event

    """
    def check(s):
        # get the value from the dict or assign None if missing
        val = dic.get(s)
        if(val): 
            return val
        else: 
            return None

    ev = Event(**{key:check(key) for key in ["name", "attributes", "data", "function"]}, flag = flag)
    return ev
