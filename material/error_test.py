#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This python module provides function to call all 54 methods
# of the RFC_RAISE_ERROR function module and stores the results
# (the caught exceptions) in the dictionaries result and result_print.
# Furthermore, it checks whether the alive-status is correct after
# the exception handling. To do so, the RFC_PING function module is
# called afterwards.
#
# Usage: From an interactive python console, import the module via
#        from error_test import *

import pyrfc
from pyrfc import RFCError, ExternalRuntimeError, CommunicationError
from config import params_connection

result = {}
methods = range(1, 54)
#methods = range(1, 20)
messagetypes = ['E']# , 'W', 'S', 'I']

def run_error():
    for method in methods:
        for messagetype in messagetypes:
            with pyrfc.Connection(**params_connection) as connection:
                ex = None
                try:
                    print "Call RFC_RAISE_ERROR with METHOD={} / MESSAGETYPE={}".format(method, messagetype),
                    connection.call("RFC_RAISE_ERROR", METHOD=str(method), MESSAGETYPE=messagetype)
                    raise RFCError("No error occured.")
                except RFCError as e:
                    ex = e
                alive = True
                try:
                    connection.call("RFC_PING")
                except ExternalRuntimeError as ert:
                    alive = False
                except CommunicationError as ce:
                    print "<CommErr>",
                    alive = False
                print "... alive={}".format(alive)
                result["{}_{}".format(method, messagetype)] = (ex, alive)

def get_exc_desc(ex, alive=None):
    ex_type_full = str(type(ex))
    ex_type = ex_type_full[ex_type_full.rfind(".")+1:ex_type_full.rfind("'")]
    code = ex.code if hasattr(ex, 'code') else '<None>'
    key = ex.key if hasattr(ex, 'key') else '<None>'
    alive = alive if alive is not None else '<None>'
    return "{}-{}-{}-{}-{}".format(ex_type, code, key, ex.message, alive)


def print_error():
    result_print = {}
    for method in methods:
        for m in messagetypes:
            key = "{}_{}".format(method, m)
            result_print[key] = "{}".format(get_exc_desc(*result[key]))

# usage: run_error(), print_error()