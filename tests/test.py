import matplotlib.pyplot as plt
from expy import Event, Experiment, plot_stack, read_fullprof_prf
if __name__ == '__main__':
    filename = 'tests/on_SiO2_Sputtered_Sn1.txt'
    filename2 = 'tests/SnSe2_100.dat'
    filename3 = 'tests/on_SiO2_C1.txt'
    filename4 = 'tests/8001_5_Survey.txt'
    filename5 = 'tests/SnSe2_Se.prf'
    ev = Event(filename4, header = "casaxps")
    # ev2 = Event(filename2, header = "fityk")
    # ex = Experiment()
    # ex.load_data([filename, filename4, filename3], folder = False, header = "casaxps")
    # print(ev)
    # print(ev.data)
    # print(ev.function_flat)
    # plot_stack(ex, shift = 8, factor = 2,  bg_pattern = None, ftot_plot = None)
    # plt.show()
    print(read_fullprof_prf(filename5))
    # print(ev2.data)

