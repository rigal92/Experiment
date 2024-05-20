

if __name__ == '__main__':
	from expy.experiment import Experiment
	ex = Experiment("test")
	ex.load_data("tests/data_short", folder = True, extension = ".dat")
	ex.load_peaks("tests/data_short")
	ex.to_json_file("tests/out_test.json")
	ev = ex["Spot3_G_P17"]
	print(ex)
