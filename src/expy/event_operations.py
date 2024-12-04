import numpy as np
import pandas as pd 
import re

import scimate.mathtools as mt


# -----------------------------------------------------------------
# Edit event.data
# -----------------------------------------------------------------
def normalize(data,ref = "y",exclude = "x"):
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
    df = data.copy()

    if (exclude is None):
        cols = df.columns
    else:
        if(not isinstance(exclude,list)):
            exclude = [exclude]
        cols = ~df.columns.isin(exclude)

    df.loc[:,cols] = mt.normalize(df.loc[:,cols],ref)
    # cols = list(set(df.drop(exclude,axis = 1,errors = "ignore").columns))
    # print(df[cols])
    # print(mt.normalize(df[cols],ref).columns)
    # df[cols] = mt.normalize(df[cols],ref)
    return df

def background_dep(data, pattern = "Bg"):
    """
    DEPRECATED
    Adds a background column to the data matching the **pattern**

    Input
    -----------------------------------------------------------------
    data: array, DataFrame
        data to obtain the background.
    pattern: str or list, default "bg"
        Selects the columns matching pattern using re.match. If pattern is a list of 
        strings all the elements will be matched
    Return

    """
    #convertinf string to list
    if(isinstance(pattern,str)):
        pattern = [pattern]

    #select all the columns matching ant pattern and sum by rows    
    truth_table = [[bool(re.match(j,i)) for i in data.columns] for j in pattern]
    bg = data.loc[:,np.any(truth_table,axis = 0)].sum(axis = 1)

    # # adds new column (col_name has to be in the signature)
    # # docstring
    # #     col_name: str
    # #         name of the new background column
    # data[col_name] = bg
    return bg


def background(data, pattern = "Bg", drop = False):
    """
    Creates a background matching data columns to the **pattern**

    Input
    -----------------------------------------------------------------
    data: array, DataFrame
        data to obtain the background.
    pattern: str (regular expression), default "bg"
        Selects the columns matching pattern (regular expression) 
        using re.search.
    drop: bool, default : False
        if True drops the colummns used to model the background
    Return
    -----------------------------------------------------------------
    tuple: 
        - First element: Series. The computed background
        - Second element: list of column names matching the pattern

    """
    df = data.filter(regex = pattern)
    bg = df.sum(axis = 1)
    columns = list(df)
    if(drop):
        df.drop(columns, axis = 1, inplace = True)

    return (bg, columns)


def read_casaxps(file):
    """
    Read file as a casaxps ASCII file.
    
    Inputs
    -----------------------------------------------------------------
    file: str
        file name
    Returns
    -----------------------------------------------------------------
    tuple
        tuple of pd.DataFrame with the data and the functions tables
        (data, function)

    """

    with open(file) as f:
        next(f)
        
        #get additional attributes
        pars = next(f).strip().split("\t")
        attributes = {}
        for i in ['Characteristic Energy eV', 'Acquisition Time s']:
            try:
                attributes[i] = float(pars[pars.index(i)+1])    
            except:
                pass


        d = {}
        for i in f:
            if(i.startswith("K.E.")):
                break        
            pars = i.strip().replace("\t\t","\t").split("\t")
            try:
                pars[1:] = [float(i) for i in pars[1:]]
            except ValueError:
                pass
            d[pars[0]]=pars[1:]
    if any(d.values()):
        funcs = pd.DataFrame(d)
        funcs = funcs.rename(columns={"Name":"fname"})
    else:
        funcs = None
    
    data = pd.read_table(file, skiprows=len(d)+2).dropna(axis=1)
    c = data.columns
    data.columns = map(str.replace, c, "."*len(c), "_"*len(c))
    # remove CPS columns
    data = data.loc[:,:"B_E_"] 
    # renaming and moving useful columns
    data = data.rename(columns = {"Counts":"y", "Envelope":"ftot", "B_E_":"x"})
    data.insert(0, "x",data.pop("x"))

    return data, funcs, attributes

