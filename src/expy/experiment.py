import numpy as np
import pandas as pd
import pickle
import json

#local import
from expy.event import Event
from expy.support import strip_path,folder_to_files
from expy.plotter import plot_stack

sort_key_Pid = lambda x:x[1].attributes["Pid"]
sort_key_P = lambda x:x[1].attributes["P"]

#should it be a dictionary i.e. a dictionary of events each event has a name 
class Experiment(dict):

    def __init__(self, name = ""):
        super().__init__()
        self.name = name
        self.functions = None
        self.functions_flat = None

    # -----------------------------------------------------------------
    # Operations on dictionary
    # -----------------------------------------------------------------

    def summary(self):
        print(f"Experiment: {self.name} \n{len(self)} events found")

    def tidy_functions(self,extra = "all", inplace = True):
        """
        Assign self.functions to a DataFrrame with all the event functions
        attached.

        Input 
        -----------------------------------------------------------------
        extra: None, str or list, default "all"
            Columns to be added to the table. Allowed values are:
            - "all" adds a column with self.name and one for each element
              in self.attributes
            - "minimal" adds P and errP(if present) columns 
            - None returns self.function
            - str will be match with either self.name or a value in 
              self.attributes. Missing columns will be skipped
            - list as for the point above but for a list of str
        inplace: bool, default: True
            modify the value inplace if True. return the function tables otherwise

        """
        functions = pd.concat([event.get_function_table(extra) for event in self.values()])
        functions.reset_index(drop = True, inplace = True)
        functions_flat = pd.DataFrame([event.get_function_flat(extra) for event in self.values()])
        if inplace:
            self.functions = functions
            self.functions_flat = functions_flat
        else:
            return functions, functions_flat
    



    # -----------------------------------------------------------------
    # Loaders
    # -----------------------------------------------------------------

    def load_data(self, files, folder = True, extension = "", header = "Fityk"):
        """
        Create events for each file.

        Input
        -----------------------------------------------------------------
        files: str or list
            file or folder names. It can be a list of filenames
        folder: bool, default = True 
            if True the string will be consider as a folder, otherwise as a file 
        extension: str, default = ""
            can specify the file extension when files is a folder name 
        header: str, default = Fityk
            can specify the header format to pass to load_data

        """
        if(folder):
            #lists files if a folder is given instead of a list of files
            files = folder_to_files(files,extension)
        else:
            #if a single file name is given then make it a list 
            if(isinstance(files, str)):
                files = [files]


        for f in files:
            #strip the file name and create an event with the name 
            name = strip_path(f)
            if(name not in self):
                ev = Event(f)
                self[ev.name] = ev
            else:
                self[name].get_data(f,header = header)

    def load_peaks(self,files, folder=True, extension=".peaks", errors=True, rename_data_columns=True):
        """
        Matches function files to the events. If extension .peaks is used,
        files are assumed to be fityk function files.

        Input
        -----------------------------------------------------------------
        files: str or list
            file or folder names. It can be a list of filenames
        folder: bool, default = True 
            if True the string will be consider as a folder, otherwise as a file 
        extension: str, default = ".peak"
            can specify the file extension when files is a folder name
        errors: bool, default True
            adds function error parameters from file  
        rename_data_columns: bool, default = True
            calls the function rename_data_columns of Event. Works only if the 
            extension is ".peaks" (Fityk functions table)

        Return 
        -----------------------------------------------------------------
        No return
        """

        if(folder):
            files = folder_to_files(files,extension)
        else:
            #if a single file name is given then make it a list 
            if(isinstance(files, str)):
                files = [files]

        not_found = []
        for f in files:
            name = strip_path(f)
            if(not name in self): 
                not_found += [name]

            elif(extension == ".peaks"):
                self[name].read_fityk(f, errors)
                self[name].rename_data_columns()

        if(not_found):
            print(f"{len(not_found)} files did not find a match when loading peaks.")
            print(*not_found, sep = "\n")

        self.tidy_functions()

    def load_pressure(self,pfile,col_name = 0, col_value = 1, col_errors = -1,force_reload = False,**args):
        """
        Read a pressure file and try to match the event name or Pid with 
        a pressure in the file. If P is already present in self.attributes  

        Input
        -----------------------------------------------------------------
        pfile: str 
            File name
        col_name: int
            index of the column containing the filename of pressure name 
            to match
        col_value: int
            index of the column containing the value of pressure 
        col_errors: int
            index of the column containing the pressure error. Negative 
            values indicate no errors
        force_reload: bool, default = False
            True will not consider if P is already present in self.attributes
        args: 
            named arguments to be passed to pd.read_table 
        """
        pressures = pd.read_table(pfile, **args)
        for i in self.values():
            #check if P is already present in the attributes unless force_reload is present
            if("P" in i.attributes and (not force_reload)):
                continue

            #first try to see if the event name matches any instances of the pressure file. 
            #otherwise try to match Pid
            if(i.name in pressures.iloc[col_name]):
                match = pressures.loc[pressures.iloc[col_name] == i.name]
            else:
                pid = i.attributes.get("Pid")
                if(pid is not None):
                    #check if the pid is present in the pressure name 
                    match = pressures.loc[[pid in x for x in pressures.iloc[:,col_name]]]
                else: 
                    match = None
            if(match is None):
                print(f"No matches found for {i.name}.")
            elif(len(match) >1):
                print(f"Multiple matches for {i.name}. Exact match can not be determined.")
            else:
                i.attributes["P"] = match.iloc[0,col_value]
                if(col_errors>=0): i.attributes["errP"] = match.iloc[0,col_errors]
        self.tidy_functions()



    # -----------------------------------------------------------------
    # File out 
    # -----------------------------------------------------------------

    # binary out
    def save_pickle(self,filename):
        """
        Save the Experiment as binary.  
        --------------------------
        DEPRECATED
        Replace with saving and reading using json. More stable and human
        readable. 
        Use for experiments saved using experiment v1.0.0
        --------------------------
        Input
        -----------------------------------------------------------------
        filename: str 
            Name of the file

        """
        with open(filename,"wb") as f:
            pickle.dump(self,f)

    # functions to csv
    def export_functions(self, filename, sep = "\t", index = False, **args):
        """
        Exports the DataFrame containing the functions using pandas.to_csv

        Input
        -----------------------------------------------------------------
        filename: str
            Name of the file 
        sep: str
            column separator
        index: bool
            Print or not the row index
        args:
            arguments of pandas.to_csv
        """
        if(self.functions is None):
            print("No functions have been loaded.")
        elif(isinstance(self.functions,pd.DataFrame)):
            self.functions.to_csv(filename, index = index, sep = sep, **args)

    # functions to csv
    def export_functions_flat(self, filename, sep = "\t", index = False, **args):
        """
        Exports the DataFrame containing the functions_flat using pandas.to_csv

        See export_functions for more details.
        """
        if(self.functions_flat is None):
            print("No functions have been loaded.")
        elif(isinstance(self.functions_flat,pd.DataFrame)):
            self.functions_flat.to_csv(filename, index = index, sep = sep, **args)

    # json out
    def to_json(self,**kwds):
        """
        Returns a json string. **kwds** can be passed to json.dumps 
        """
        return json.dumps({key:value.to_dict() for key,value in self.items()},**kwds) 

    # json file out
    def save(self,filename, indent = "\t", **kwds):
        """
        Save to a json file. 
        Input
        --------------------------
        filename: str
            file name to save
        indent: str
            formatting option for the indentation in json.dump
        kwds:
            passed to json.dump 


        """
        if(not filename.endswith(".json")):
            filename += ".json"
        with open(filename,"w") as f:
            return json.dump({key:value.to_dict() for key,value in self.items()},f, indent = indent, **kwds) 

    def __repr__(self):
        return "-"*30 + "\n" + "\n".join([f"{v}\n" + "-"*30 for v in self.values()])