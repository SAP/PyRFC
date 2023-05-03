def enum_names(enum_obj):
    """Enum object names."""
    return {en.name for en in enum_obj}


def enum_values(enum_obj):
    """Enum object values."""
    return {en.value for en in enum_obj}
