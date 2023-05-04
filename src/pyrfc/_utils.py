# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0


def enum_names(enum_obj):
    """Enum object names."""
    return {en.name for en in enum_obj}


def enum_values(enum_obj):
    """Enum object values."""
    return {en.value for en in enum_obj}
