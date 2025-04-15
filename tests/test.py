import matplotlib.pyplot as plt
from expy import Event, Experiment, plot_stack, plot_event, read_fullprof_prf, read_fityk
from fityk import Fityk
if __name__ == '__main__':
    filename = 'tests/on_SiO2_Sputtered_Sn1.txt'
    filename2 = 'tests/SnSe2_100.dat'
    filename3 = 'tests/on_SiO2_C1.txt'
    filename4 = 'tests/8001_5_Survey.txt'
    filename5 = 'tests/SnSe2_Se.prf'
    filename6 = 'tests/data/fit.fit'
    # ev = Event(filename, header = "casaxps")

    # f = Fityk()
    # f.execute(f"reset; exec {filename6}")
    ex = read_fityk(filename6)
    print(ex)

    ev2 = Event(filename2, header = "fityk")
    # print(ev2.function)
    # print(ev2.data)
    # ex = Experiment()
    # ex.load_data([filename, filename4, filename3], folder = False, header = "casaxps")
    # print(ev)
    # print(ev.data)
    # print(ev.function_flat)
    # plot_event(df, x = "2Theta",  normalized = "Ycal",  bg_pattern = None, y_plot = None, ftot_plot = None)
    # plot_event(ev.data,  normalized = {"ref":"y", "exclude":"x"},  bg_pattern = None, y_plot = None, ftot_plot = None)
    # plt.show()

