import pickle

def enum_names(enum_obj):
    return set(e.name for e in enum_obj)


def enum_values(enum_obj):
    return set(e.value for e in enum_obj)


def py_to_string(obj):
    return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)


def string_to_py(objstr):
    return pickle.loads(objstr)
