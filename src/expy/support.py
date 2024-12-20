import os 

def strip_path(path, extension = None):
    """
    remove file path and extension from a filename
    """

    name = path.split("/")[-1]
    if extension is not None:
        name = name.removesuffix(extension)
    return name


def folder_to_files(folder,extension):
    """
    checks if the folder path ends with slash and meke a list of files by extension
    """
    folder = folder +"/" if not folder.endswith("/") else folder
    return [folder + f for f in os.listdir(folder) if f.endswith(extension)]

def accept_event_flags(flag, accepted):
    """
    Check good flags formatting. 

    """
    if flag == None:
    	return []
    if not isinstance(flag,list):
        flag = [flag]
    bad = [x for x in flag if x not in accepted]
    if len(bad)>0:
        bad = ",".join(bad)
        print(f"Warning: Unknown flags [{bad}]. Ignoring those flags.")
    return flag