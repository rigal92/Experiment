import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import json
import re

import scimate.mathtools as mt

#local imports 
from .support import strip_path
from .plotter import plot_event
from .event_operations import *

def tokenize(string, char = "_"):
    """
    Split the file name in individual tokens that can have important information 
    a special tocken is Pid that is given by a tocken starting with P and followed by a namber 

    Input
    -----------------------------------------------
    string:str
        Input string to tokenize
    char: str
        Character used to split

    Output
    -----------------------------------------------
    dict
        Dictionary of the tokens

    """
    s = string.split(char)
    tokens = {}
    count = 0
    for i in s:
        if(i.startswith("P") and not ("Pid" in tokens)):
            tokens["Pid"] = i
        else:
            tokens[f"T{count + 1}"] = i
            count +=1
    return tokens

def read_event(dic):
    """
    Parse keywords from a dictionary and creates an event.
    """
    ev = Event()
    ev.name = dic.get("name")
    ev.attributes = dic.get("attributes")
    ev.function = pd.DataFrame(dic.get("function"))
    ev.data = pd.DataFrame(dic.get("data"))
    return ev


 
class Event:
    """
    Event class gathering in a dictionary the data and fit results
    """
    def __init__(self, data = None,tokenby = "_"):
        """
        Input
        -----------------------------------------------------------------
        data: str or DataFrame
            If str it should be a file name of data without header. Else 
            self.data will be assigned to the DataFrame
        tokenby: str , default is "_"
            Character used by tokenize
        """
        if(isinstance(data,str)):
            self.get_data(data)
            #remove file folder path and file type
            self.name = strip_path(data)
            self.attributes = tokenize(self.name)
        else:
            self.name = None
            self.attributes = None
            self.data = data
        self.function = None


    # -----------------------------------------------------------------
    # Edit self.data
    # -----------------------------------------------------------------
    def normalize(self,ref = "y",exclude = "x"):
        """
        Normalize data to its maximum value. Ref can be used to notmalize 
        to the maximum of a specific column of a DataFrame.

        Input
        -----------------------------------------------------------------
        data: array, DataFrame
            data to be normalized.
        ref: None or string, default None
            for DataFrames a specific column can be selected giving the 
            column name in ref. If None is given the maximumm of the data 
            frame will be used.
        exclude : None, str or list, default "x"
            exclude some columns from the normalization. Those will be 
            left unchanged on the returned DataFrame 
        Return
        -----------------------------------------------------------------
        DataFrame:
            Normalized indensities

        """
        df = self.data.copy()

        if (exclude is None):
            cols = df.columns
        else:
            if(not isinstance(exclude,list)):
                exclude = list(exclude)
            cols = ~df.columns.isin(exclude)

        df.loc[:,cols] = mt.normalize(df.loc[:,cols],ref)
        # cols = list(set(df.drop(exclude,axis = 1,errors = "ignore").columns))
        # print(df[cols])
        # print(mt.normalize(df[cols],ref).columns)
        # df[cols] = mt.normalize(df[cols],ref)
        return df

    def background(self, pattern = "Bg", col_name = "bg_tot"):
        """
        Adds a background column to the data matching the **pattern**

        Input
        -----------------------------------------------------------------
        pattern: str or list, default "bg"
            Selects the columns matching pattern using re.match. If pattern is a list of 
            strings all the elements will be matched 
        col_name: str
            name of the new background column
        """
        #convertinf string to list
        if(isinstance(pattern,str)):
            pattern = [pattern]

        #select all the columns matching ant pattern and sum by rows    
        truth_table = [[bool(re.match(j,i)) for i in self.data.columns] for j in pattern]
        new_col = self.data.loc[:,np.any(truth_table,axis = 0)].sum(axis = 1)

        #adds new column
        self.data[col_name] = new_col

    def rename_data_columns(self):
        """
        Rename standard column fityk names to the functions names in self.function
        """
        names = self.function.get("fname")
        if(isinstance(names,type(None))):
            print("Names not found. Impossible to rename, consider to add functions.")
            return
        for i,val in enumerate(names):
            self.data.rename(columns= {f"f{i}":val},inplace = True)




    # -----------------------------------------------------------------
    # Loaders 
    # -----------------------------------------------------------------

    def get_function_table(self,extra = "all"):
        """
        Return function table where extra columns can be added. 

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
        Return
        -----------------------------------------------------------------
        pandas.DataFrame:
            self.function with the eventual added columns

        """
        #check that self.function contains a function table
        if(self.function is None):
            print(f"WARNING! {self.name} does not contain any functions. Ignored")
            return pd.DataFrame()
            
            
        if(extra is None):
            return self.function

        if(extra == "all"):
            #order of columns will be inverted when doing insert so name is last
            cols = list(self.attributes.items()) + [("name",self.name)] 
        elif(extra=="minimal"):
            cols = [("errP" , self.attributes.get("errP")) if "errP" in self.attributes else None,("P" , self.attributes.get("P")),("name",self.name)] 
        else:
            if(isinstance(extra,str)):
                #if a single string is inserted make it a list 
                extra = [extra]
            #
            cols = [(label,self.attributes[label]) if label in self.attributes else None for label in extra] + [("name",self.name)] 

        df = self.function.copy()
        # df.insert(0,"name",self.name)
        [df.insert(0,x[0],x[1]) if x is not None else None for x in cols]
        return df


    def get_data(self,filename,header = "Fityk"):
        """
        Read a file containing data in columns. A header can be specified.
        
        Input
        -----------------------------------------------------------------
        filename: str
            Input file
        header: 
            Build header in "Fityk" format or as pandas.read_table 

        """

        #read the data file. Except the case in which the header tipe is wrong. "Fityk" also falls in this case 
        try:
            df = pd.read_table(filename,header = header,sep = " ")

        except ValueError:

            df = pd.read_table(filename,header = None,sep = " ")
            if(header == "Fityk"):
                   df.columns = ["x","y"] + [f"f{i}" for i in range(df.columns.size - 3)] + ["ftot"]
            else:
                print("Wrong header format. None is considered.")
        self.data = df

    def read_fityk(self,filename, errors = True):
        """
        Reads a .peak fityk file and adds it to event as "fit"

        Input
        -----------------------------------------------
        filename:str
            file containg the fit results
        errors:bool
            read or not the parameters error
        Returns
        -----------------------------------------------
        pandas.DataFrame:
            DataFrame containing the functions identidier, name and parameters  


        """
        #x is used for the quantities that do not have clearly defined one of the standard parameters (Center,Height...). They will be replaced by NaN
        df = pd.read_table(filename,na_values = "x")

        #split function name and id 
        # df.insert(0,"name",self.name)
        df.insert(1,"fid",[x.split()[0] for x in df.loc[:,"# PeakType"]])
        df.insert(2,"fname",[x.split()[1] for x in df.loc[:,"# PeakType"]])

        #split the parameters that are placed all together by Fityk and replace ? by 0 for unknown errors 
        pars = pd.DataFrame([map(float,x.replace("+/-","").replace("?","0").split()) for x in df.loc[:,"parameters..."]])
        if(errors):
            pars.columns = [f"a{int(i/2)}" if (not i%2) else f"err_a{int(i/2)}" for i in range(len(pars.columns))]
        else:
            pars.columns = [f"a{i}" for i in range(len(pars.columns))]

        #adds the parameters 
        df = df.join(pars)

        #drop useless columns 
        df.drop(columns = ["# PeakType",'parameters...'],inplace = True)

    
        #add the functions dataframe and calculates the 
        self.function = df


    # -----------------------------------------------------------------
    # Input/output
    # -----------------------------------------------------------------


    def to_json(self):
        return json.dumps(self.to_dict())

    # -----------------------------------------------------------------
    # Conversions
    # -----------------------------------------------------------------

    def to_dict(self):
        dic = {
            "name":self.name,
            "attributes":self.attributes,
            "function":self.function.to_dict() if isinstance(self.function,pd.DataFrame) else self.function,
            "data":self.data.to_dict() if isinstance(self.data,pd.DataFrame) else self.data

        }
        return dic



def main():
    filename = 'tests/RBM_P02:1:4.dat'
    filename2 = 'tests/RBM_P02:1:4.peaks'
    ev = Event(filename)
    ev.read_fityk(filename2)
    names = ev.function.fname

    ev.rename_data_columns()

    # print(ev.data)
    # bg, labs = background(ev.data)
    plot_event(ev.data)
    plt.show()
    # print(ev.data.filter(regex = "bg"))


    # plt.figure()
    # plt.plot(ev.data.bg_tot)
    # plt.plot(ev.data.Bg1)
    # plt.plot(ev.data.Bg2)
    # plt.figure()
    # plt.plot(ev.data.bg_tot - ev.data.Bg1 - ev.data.Bg2)
    # plt.plot(ev.data.bg_tot - ev.data.bg_tot)
    # plt.show()

    # print(ev.data.x,"\n",ev.normalize().x)



# if __name__ == '__main__':
#     filename = 'tests/Spot1_G_P00.dat'
#     filename2 = 'tests/Spot1_G_P00.peaks'
#     ev = Event(filename)
#     ev.read_fityk(filename2)
#     print(ev.function.columns)
#     print(ev.data.columns)