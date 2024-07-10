from expy import Event, Experiment
if __name__ == '__main__':
    filename = 'tests/on_SiO2_Sputtered_Sn1.txt'
    filename2 = 'tests/SnSe2_100.dat'
    filename3 = 'tests/Surv.csv'
    filename4 = 'tests/8001_5_Survey.txt'
    ev = Event(filename4, header = "casaxps")
    # ev2 = Event(filename2, header = "fityk")
    # ex = Experiment()
    # ex.load_data([filename3, filename4], folder = False, header = 1, sep = ",", skiprows = 4)
    print(ev)
    print(ev.data)
    print(ev.function_flat)
    # print(ev2.data)

