
if __name__ == '__main__':
	import expy
	import matplotlib.pyplot as plt
	from expy import Experiment
	ex = Experiment(name = "test")
	ex.load_data("tests/data_short", folder = True, extension = ".dat")
	ex.load_peaks("tests/data_short")
	ex.load_pressure("tests/data/Pressures")
	ev = ex["Spot3_G_P17"]
	df = ev.data
	ex.save("tests/out_test.json", indent = "\t")
	# ex1 = expy.read("tests/out_test.json")
	# ex1.save("tests/out_test2.json", indent = "\t")
	# print(set(ex.functions.fname))
	# print(ev.data)
	ex2 = ex.sort(key = lambda x:x[1].name, reverse = True)
	print(ex2.functions)
	att = ex.get_attributes()
	fig, ax = plt.subplots()
	expy.plot_stack(
		ex,
		bg_pattern = "Lorentz",
		to_background = None, 
		ftot_plot = None,
		ax = ax,
		sort = expy.experiment.sort_key_Pid,
		other_plot = {"Air":{"c":"k"}, "_rem":{"pos":["-"],"c":[0,.3957,.6043], "alpha":.3}},
		labels = "P",
		labels_format = ".2f",
		ylabels_shift = 0
		)
	plt.show()
	print(ex)