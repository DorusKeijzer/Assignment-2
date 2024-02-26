import inspect
import cv2 as cv

def var_name_to_string(var, caller_locals):
    for name, value in caller_locals.items():
        if value is var:
            return name
    return None

def debugMatrices(*args):
    """Prints the dimensions and type of all matrices you give as arguments"""
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals
    for arg in args:
        var_name = var_name_to_string(arg, caller_locals)
        if var_name:
            print(f"{var_name} {arg.shape} {arg.dtype}")
        else:
            print(f"Can't determine shape of {var_name}\n")

def readXML(path, *args):
    """Imports the specified variables from the xml file at path"""
    fs = cv.FileStorage(path, cv.FILE_STORAGE_READ)
    res = []
    for arg in args:
        try:
            res.append(fs.getNode(arg).mat())
        except:
            pass
    fs.release()
    return res
