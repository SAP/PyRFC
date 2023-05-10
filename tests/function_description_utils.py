# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from pyrfc import Connection

parameter_keys = [
    "name",
    "parameter_type",
    "direction",
    "nuc_length",
    "uc_length",
    "decimals",
    "default_value",
    "optional",
    "type_description",
    "parameter_text",
]

typedesc_keys = [
    "name",
    "field_type",
    "nuc_length",
    "nuc_offset",
    "uc_length",
    "uc_offset",
    "decimals",
    "type_description",
]


def compare_function_description(fd1, fd2):
    # compare names
    fd1_name = fd1["name"] if type(fd1) is dict else fd1.name
    fd2_name = fd2["name"] if type(fd2) is dict else fd2.name
    # print(fd1_name, len(fd1_name))
    # print(fd2_name, len(fd2_name))
    assert fd1_name == fd2_name
    # compare parameters
    fd1_parameters = fd1["parameters"] if type(fd1) is dict else fd1.parameters
    fd2_parameters = fd2["parameters"] if type(fd2) is dict else fd2.parameters
    # print(len(fd1_parameters))
    # print(len(fd2_parameters))
    assert len(fd1_parameters) == len(fd2_parameters)
    for param1, param2 in zip(fd1_parameters, fd2_parameters):
        for key in parameter_keys:
            if key != "type_description":
                assert param1[key] == param2[key]
        if param1["type_description"] is None:
            assert param2["type_description"] is None
        else:
            # compare fields
            fd1_fields = (
                param1["type_description"]["fields"]
                if type(param1["type_description"]) is dict
                else param1["type_description"].fields
            )
            fd2_fields = (
                param2["type_description"]["fields"]
                if type(param2["type_description"]) is dict
                else param2["type_description"].fields
            )
            assert len(fd1_fields) == len(fd2_fields)
            assert fd1_fields == fd2_fields


def function_description_to_dict(func_desc):
    FDD = {
        "name": func_desc.name,
        "parameters": [],
    }
    for parameter in func_desc.parameters:
        # print("parameter", parameter, parameter["type_description"])
        param = {}
        for key in parameter_keys:
            if key == "type_description" and parameter[key] is not None:
                param[key] = {
                    "name": parameter[key].name,
                    "fields": parameter[key].fields,
                }
            else:
                param[key] = parameter[key]
        FDD["parameters"].append(param)
    return FDD


# function description test data
def main(func_name):
    # from data.func_desc_BAPISDORDER_GETDETAILEDLIST import FUNC_DESC_BAPISDORDER_GETDETAILEDLIST
    # from data.func_desc_BS01_SALESORDER_GETDETAIL import FUNC_DESC_BS01_SALESORDER_GETDETAIL

    from data.func_desc_STFC_STRUCTURE import FUNC_DESC_STFC_STRUCTURE  # noqa: E402 WPS131

    with Connection(dest="MME") as client:
        func_desc = client.get_function_description(func_name)
    fd = function_description_to_dict(func_desc)
    # print(fd) # > fd.py
    compare_function_description(
        fd,
        FUNC_DESC_STFC_STRUCTURE,
    )
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No function name provided.")
        sys.exit()
    main(sys.argv[1])
