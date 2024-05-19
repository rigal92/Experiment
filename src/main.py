#!/usr/bin/env python3

from expy.experiment import Experiment, plot_stack, sort_key
import matplotlib.pyplot as plt
import expy.event as evt


#test folder
folder = "tests/"
# file = "Spot1_G_P00.dat"

if __name__ == '__main__':
    ex = Experiment("ciccio")
    ex.load_data(folder,folder = True,extension = ".dat")
    ex.load_peaks(folder)
    sel = {key:val for key,val in ex.items() if "Spot1" in key}
    plot_stack(sel, sort = sort_key)
    plt.show()



    # ex.summary()
    # ex.load_pressure(folder +"Pressures",col_errors = 2)
    # ex.export_functions(folder + "out.func")
    # ex.tidy_functions("minimal")
    # ex.export_functions(folder + "out_min.func")
    # evt.main()
        