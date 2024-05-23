import matplotlib.pyplot as plt 
import pandas as pd
from .event_operations import *
from copy import deepcopy

def plot_event(
        data,
        x = "x",
        #editing parameters 
        normalized = {"ref":"y", "exclude":"x"}, 
        bg_pattern = None,
        to_background = ["y","ftot"],
        drop_bg = True,
        shift = 0,
        #plotting parameters
        axes = None,
        y_plot = {"pos":[".k"], "ms":2}, 
        ftot_plot = {"pos":["-r"]},
        other_plot = {"_rem":{"pos":["-"],"c":[0,.3957,.6043], "alpha":.3}},
        xlim = None,
        ylim = None,
        **kwargs
        ):
    """
    Plot spectrum using plt.plot.  

    Input
    -----------------------------------------------------------------
    data: pandas.DataFrame
        data to plot
    x : str, default "x"
        Variable for x axis
    normalized: dict or None, default: {"ref":"y", "exclude":"x"}
        Dictionary with the keywords for normalization. Only **ref**
        and **exclude** keywords are useful. 
        See event.Event.normalize for more information on accepted 
        keywords.
        - Missing keys will be assigned to None values
        - None or empty dictionary will not normalize the data
    bg: str (regular expression), default: None
        - if **str** finds background columns matching the string 
        (see event_operations.background)
        - if **None** no bg substraction
    to_background: None, str or list, default: ["y","ftot"]
        Column names to which the background will be substracted.
        None value will affect all the columns
    drop_bg: Bool, default: True
        avoid drawing columns used for the background substraction 
    shift: float, default: 0
        allowes for shifting the spectrum of **shift**
    y_plot: dict or None, default: {"positionals":[".k"], "ms":2}
        Plotting arguments to pass to plot for a column called "y"
        - "pos" is a list of positional arguments
        - keyword arguments can be passed specifing their keybword
        - None will not plot this columns
    ftot_plot: dict or None, default: {"positionals":["-r"]}
        Same as y_plot but for a column called "ftot"
    other: dict or None, default: {"_rem":{"pos":["-"],"c":[0,.3957,.6043], "alpha":.3}}
        Dictionary where the keys are column names patterns (re.search) 
        and the values are dictionary as for y_plot argument
        - _rem is a keyword for all the columns not explicitly 
        assigned
        - None will not consider those columns
    xlim: tuple or None, default: None
        Exclude points outside the limits given in the tuple 
        (xmin,xmax) 
    ylim: string or None, default: None
        Exclude points which do satisfy the condition given 
        by the string that will be passed to eval (python build-in).
        The condition is applied after bg substraction if present.
        USE df TO REFER TO data
        e.g.:
            ylim = "df.y > df.loc[df.x >1000 & df.x < 2000].f1.max()" 
            all the points where the column y is bigger than the 
            maximum value of the column f1 in the range 1000:2000
            are excluded  
    kwargs:
        keywords to be passed to plt.plot


    """ 
    df = data.copy()


    #remove bg
    if(bg_pattern):
        bg, labels = background(df,bg_pattern)
        if(drop_bg == True):
            df.drop(labels, axis = 1, inplace = True)
        if(to_background is None):
            #select all columns apart for x
            to_background = list(filter(lambda y:y!=x, df.columns))
        df[to_background] = df[to_background].sub(bg,axis = 0)
    #manage x limits
    if(xlim):
        if(not isinstance(xlim,tuple)):
            raise TypeError("Wrong x limit type. tuple expected.")
        else:
            low = xlim[0] if xlim[0] else df["x"].min()
            high = xlim[1] if xlim[1] else df["x"].max()
            df = df.query("(x>=@low) and (x<=@high)")
    #manage y limits
    if(ylim):
        if(not isinstance(ylim,str)):
            raise TypeError("Wrong y limit type. str expected.")
        else:
            # df = df.query("y<" + ylim)
            df.loc[eval(ylim)] = None 


    #normalize
    if(normalized):
        ref = normalized.get("ref")
        exclude = normalized.get("exclude")
        df = normalize(df, ref = ref, exclude = exclude)
    if(shift):
        df.loc[:,df.columns != x] += shift



    #plotting
    if(not axes):
        axes = plt.axes()

    x = df.pop(x)
    

    if(y_plot is not None):
        var= deepcopy(y_plot)
        axes.plot(x, df.pop("y"),*var.pop("pos",[]),**var,**kwargs)
    if(ftot_plot is not None):
        var= deepcopy(ftot_plot)
        axes.plot(x, df.pop("ftot"),*var.pop("pos",[]),**var,**kwargs)
    if(other_plot is not None):
        var = deepcopy(other_plot)
        if("_rem" not in list(df)):
            remaining = var.pop("_rem",None)
        else:
            print("WARNING! DataFrame contains _rem column")
            remaining = None
        for key,value in var.items():
            sel = df.filter(regex = key)
            axes.plot(x, sel,*value.pop("pos",[]),**value,**kwargs)
            for i in set(sel.columns):
                df.pop(i)
        if(remaining is not None):
            axes.plot(x, df,*remaining.pop("pos",[]),**remaining,**kwargs)

    return axes




def plot_stack(
        experiment,
        factor = 1,
        labels = None,
        labels_format = None,
        xlabels = 1.01,
        ylabels_shift = 0,
        #sorting
        sort = None,
        reverse = False,
        x = "x",
        #data edit
        normalized = {"ref":"y", "exclude":"x"}, 
        bg_pattern = "Bg",
        to_background = ["y","ftot"],
        drop_bg = True,
        #plotting
        ax = None,
        y_plot = {"pos":[".k"], "ms":2}, 
        ftot_plot = {"pos":["-r"]},
        other_plot = {"_rem":{"pos":["-b"],"alpha":.3}},
        xlim = None,
        ylim = None,
        **kwargs
        ):
    """
    Stack plot of the events. Only the parameters specific to plot_stack
    are described. For the other inputs see plot_event.
    Inputs
    -----------------------------------------------------------------
    experiment: expy.Experiment
        the experiment to plot
    factor: float, default:1
        multiplication factor to shift the data
    labels: str, list or None, default: None
        if different from None it adds text at each plot edge.  
        Accepted values:
        - str indicating the attribute name to use
        - list of string. It must be of the same length of experiment.
          Sorting will not affect this list  
    labels_format: str or None, default: None
        formats labels using format. egs: labels_format='.2f'
    xlabels: fload, default: 1.01
        x postition of the labels in axes coordinates. 1.01 is on the 
        outside of the edge on the right side
    ylabels_shift: float, default: 0
        y shift of each label from the 0 of the plots 
    sort: function or None, default: None
        key to be passed to sorted for custom sorting of the plots
    reverse: bool, default:False
        allows to reverse the order of sort

    """
    

    if (sort):
        experiment = experiment.sort(key = sort, reverse = reverse)
    if(isinstance(labels, str)):
        try:
            labels = experiment.get_attributes()[labels]
        except KeyError:
            print(f"KeyError: No attibutes named {labels} available. Skipping stack plot labelling.")
            labels = None
    elif(isinstance(labels, list)):
        if len(labels) != len(experiment):
            raise ValueError("the length of labels is not matching the length of experiment.")
    if labels_format and (not isinstance(labels, type(None))):
        try:
            labels = list(map(format, labels, [labels_format]*len(labels)))
        except:
            print("Warning! Formatting of the labels was not possible. Skipping.")


    if (not ax):
        ax = plt.axes()
    for i,val in enumerate(experiment.values()):
        plot_event(val.data,
            x = x,
            normalized =  normalized,
            bg_pattern = bg_pattern,
            to_background = to_background,
            axes = ax,
            shift = i * factor,
            y_plot= y_plot,
            ftot_plot= ftot_plot,
            other_plot= other_plot,
            xlim = xlim,
            ylim = ylim,
            **kwargs
            )
        if(not isinstance(labels,type(None))):
            ax.text(xlabels, i*factor + ylabels_shift, labels[i], transform = ax.get_yaxis_transform())
    return ax


