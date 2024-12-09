if __name__ == '__main__':
	from expy.experiment import Experiment

	ex = Experiment("test")
	ex.load_data("tests/data", folder = True, extension = ".dat")
	ex.load_peaks("tests/data")
