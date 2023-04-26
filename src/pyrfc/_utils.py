import pickle


def enum_names(enum_obj):
    """Enum object names."""
    return {e.name for e in enum_obj}


def enum_values(enum_obj):
    """Enum object values."""
    return {e.value for e in enum_obj}


def py_to_string(obj):
    """Serialize Python object to string."""
    return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)


def string_to_py(objstr):
    """Create Python object from string."""
    return pickle.loads(objstr)
