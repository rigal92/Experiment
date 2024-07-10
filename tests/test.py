from expy import Event, Experiment
if __name__ == '__main__':
    filename = 'tests/on_SiO2_Sputtered_Sn1.txt'
    filename2 = 'tests/SnSe2_100.dat'
    filename3 = 'tests/Surv.csv'
    filename4 = 'tests/Surv_sputtered.csv'
    ev = Event(filename, header = 7)
    ev2 = Event(filename2, header = "fityk")
    ex = Experiment()
    ex.load_data([filename3, filename4], folder = False, header = 1, sep = ",", skiprows = 4)
    print(ex)
    print(ev.data)
    # print(ev2.data)

