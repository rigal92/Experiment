import os 

def strip_path(path):
	"""
	remove file path and extension from a filename
	"""
	return path.split("/")[-1].split(".")[0]


def folder_to_files(folder,extension):
	"""
	checks if the folder path ends with slash and meke a list of files by extension
	"""
	folder = folder +"/" if not folder.endswith("/") else folder
	return [folder + f for f in os.listdir(folder) if f.endswith(extension)]