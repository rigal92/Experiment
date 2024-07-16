import json 
import pickle
import os
import pandas as pd

from expy import Experiment, Event

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

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
        See Event for allowed values 
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

def get_notebook_template(folder = "./"):
    import shutil
    path = os.path.join(folder,"Experiment.ipynb")
    if(os.path.exists(path)):
        print("Warning!", path, "already exists. Skipping this file.")
    else:
        shutil.copyfile(os.path.join(ROOT_DIR, "jupyter/Standard.ipynb"), path)
    path = os.path.join(folder,"LabNotes.mb")
    if(os.path.exists(path)):
        print("Warning!", path, "already exists. Skipping this file.")
    else:
        shutil.copyfile(os.path.join(ROOT_DIR, "jupyter/LabNotes.md"), path)


def read_fullprof_prf(filename, header = 4, **kargs):
    """
    Read fullprof prf file.
    
    Input
    -----------------------------------------------------------------
    filename, str
        name of the file
    header, 
        format of the header as for pandas read_table
    **kargs:
        other keyword args to be passed to pandas read_table

    """
    df = pd.read_table(filename, header = header)
    df.Yobs = pd.to_numeric(df.Yobs, errors="coerce")
    return df.dropna(how="any", subset = "Yobs", axis = 0).dropna(axis = 1)


