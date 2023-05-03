def enum_names(enum_obj):
    """Enum object names."""
    return {e.name for e in enum_obj}


def enum_values(enum_obj):
    """Enum object values."""
    return {e.value for e in enum_obj}
