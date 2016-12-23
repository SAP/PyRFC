#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
import pyrfc, unittest
from pyrfc import TypeDescription, FunctionDescription, Server, \
                      RFCError, ABAPApplicationError, ABAPRuntimeError, \
                      ExternalRuntimeError

from pyrfc._pyrfc import _Testing
from configparser import ConfigParser

config = ConfigParser()
config.read('pyrfc.cfg')

# Server functions
def my_stfc_connection(request_context, REQUTEXT):
    return {
        'ECHOTEXT': REQUTEXT,
        'RESPTEXT': u"Local server here."
    }

def my_stfc_changing(request_context, START_VALUE, COUNTER):
    return {
        'COUNTER': COUNTER + 10,
        'RESULT': START_VALUE + (COUNTER + 10)
    }

def my_sftc_connection_error(request_context, REQUTEXT):
    # depending on the REQUTEXT value, raises errors.
    if REQUTEXT == 'EXCEPTION':
        raise ABAPApplicationError(key='BAD_EXCEPTION_HAPPENED')
    elif REQUTEXT == 'EXCEPTION_MESSAGE':
        raise ABAPApplicationError(key='BAD_EXCEPTION_W_MSG',
            msg_class='SR', # message id or class
            msg_type='E', # out of e.g. 'E', 'A' or 'X'
            msg_number='007', # 3 char numeric
            msg_v1='V1 text' # 50 char
        )
    elif REQUTEXT == 'MESSAGE':
        raise ABAPRuntimeError(
            msg_class='SM', # message id or class
            msg_type='E', # out of e.g. 'E', 'A' or 'X'
            msg_number='107', # 3 char numeric string
            msg_v1='V1 text (ABAP_MESSAGE)'
        )
    elif REQUTEXT == 'FAILURE':
        raise ExternalRuntimeError("Something very bad happened.")
    elif REQUTEXT == 'INVALID':
        raise RFCError("Invalid exception")
    return {
        'ECHOTEXT': REQUTEXT,
        'RESPTEXT': u"Local (raise error) server here. Use the following values"
                    u"for REQUTEXT: EXCEPTION, EXCEPTION_MESSAGE, MESSAGE, "
                    u"FAILURE, or INVALID."
    }

class ServerTest(unittest.TestCase):
    """
    This test cases cover the metadata modelling (TypeDescription,
    FunctionDescription) and the Server tests
    """

    @classmethod
    def setUpClass(cls):
        # print "Os cwd", os.getcwd()
        # print "Config", config
        ## print config._sections.items()
        cls.conn = pyrfc.Connection(**config._sections['connection'])

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_func_desc_manual(self):
        # Example taken from hardCodedServer (cf. Schmidt and Li, 2009c)
        animals = TypeDescription("animals", nuc_length=20, uc_length=28)
        self.assertEqual(animals.nuc_length,20)
        self.assertEqual(animals.uc_length,28)
        animals.add_field(name=u'LION', field_type='RFCTYPE_CHAR', nuc_length=5, uc_length=10, nuc_offset=0, uc_offset=0)
        animals.add_field(name=u'ELEPHANT', field_type='RFCTYPE_FLOAT', nuc_length=8, uc_length=8, decimals=16, nuc_offset=8, uc_offset=16)
        animals.add_field(name=u'ZEBRA', field_type='RFCTYPE_INT', nuc_length=4, uc_length=4, nuc_offset=16, uc_offset=24)

        i_dont_exist = FunctionDescription(u"I_DONT_EXIST")
        i_dont_exist.add_parameter(name=u"DOG", parameter_type="RFCTYPE_INT",
            direction="RFC_IMPORT", nuc_length=4, uc_length=4)
        i_dont_exist.add_parameter(name=u"CAT", parameter_type="RFCTYPE_CHAR",
            direction="RFC_IMPORT", nuc_length=5, uc_length=10)
        i_dont_exist.add_parameter(name=u"ZOO", parameter_type="RFCTYPE_STRUCTURE",
            direction="RFC_IMPORT", nuc_length=20, uc_length=28, type_description=animals)
        i_dont_exist.add_parameter(name=u"BIRD", parameter_type="RFCTYPE_FLOAT",
            direction="RFC_IMPORT", nuc_length=8, uc_length=8, decimals=16)

        self.assertEqual(len(i_dont_exist.parameters), 4)
        self.assertEqual(i_dont_exist.name, u"I_DONT_EXIST")


    def test_func_desc_auto(self):
        test = _Testing()
        func_desc = self.conn.get_function_description("STFC_STRUCTURE")
        func_desc2 = test.fill_and_wrap_function_description(func_desc)

        self.assertEqual(pickle.dumps(func_desc), pickle.dumps(func_desc2))


    def test_server(self):
        server = Server(config={'debug': True}, **config._sections['gateway'])
        test = _Testing()

        # Install two functions
        func_desc_conn = self.conn.get_function_description("STFC_CONNECTION")
        server.install_function(
            func_desc_conn,
            my_stfc_connection
        )
        func_desc_chan = self.conn.get_function_description("STFC_CHANGING")
        server.install_function(
            func_desc_chan,
            my_stfc_changing
        )

        # Lookup test
        func_desc_invalid = test.get_srv_func_desc("NOT_VALID")
        self.assertEqual(func_desc_invalid, 17, "Return code for unknown func_desc should be RFC_NOT_FOUND (17).")

        func_desc_conn2 = test.get_srv_func_desc("STFC_CONNECTION")
        self.assertEqual(pickle.dumps(func_desc_conn), pickle.dumps(func_desc_conn2))

        func_desc_chan2 = test.get_srv_func_desc("STFC_CHANGING")
        self.assertEqual(pickle.dumps(func_desc_chan), pickle.dumps(func_desc_chan2))

        # Invocation test
        result = test.invoke_srv_function("STFC_CONNECTION", REQUTEXT="request_text")
        self.assertEqual(result['ECHOTEXT'], "request_text")
        self.assertEqual(result['RESPTEXT'], u"Local server here.")

        result = test.invoke_srv_function("STFC_CHANGING", START_VALUE=23, COUNTER=7)
        self.assertEqual(result['COUNTER'], 17) # COUNTER = COUNTER + 10
        self.assertEqual(result['RESULT'], 40) # RESULT = START_VALUE + (COUNTER + 10)

        server.close()

    def test_server_error(self):
        server = Server(config={'debug': True}, **config._sections['gateway'])
        test = _Testing()

        # Install two functions
        func_desc_conn = self.conn.get_function_description("STFC_CONNECTION")
        server.install_function(
            func_desc_conn,
            my_sftc_connection_error
        )

        with self.assertRaises(ABAPApplicationError) as run:
            test.invoke_srv_function("STFC_CONNECTION", REQUTEXT="EXCEPTION")
        self.assertEqual(run.exception.code, 5, "rc")
        self.assertEqual(run.exception.key, "BAD_EXCEPTION_HAPPENED")

        with self.assertRaises(ABAPApplicationError) as run:
            test.invoke_srv_function("STFC_CONNECTION", REQUTEXT="EXCEPTION_MESSAGE")
        self.assertEqual(run.exception.code, 5, "rc")
        self.assertEqual(run.exception.key, "BAD_EXCEPTION_W_MSG")
        self.assertEqual(run.exception.msg_class, "SR")
        self.assertEqual(run.exception.msg_type, "E")
        self.assertEqual(run.exception.msg_number, "007")
        self.assertEqual(run.exception.msg_v1, "V1 text")

        with self.assertRaises(ABAPRuntimeError) as run:
            test.invoke_srv_function("STFC_CONNECTION", REQUTEXT="MESSAGE")
        self.assertEqual(run.exception.code, 4, "rc")
        self.assertEqual(run.exception.msg_class, "SM")
        self.assertEqual(run.exception.msg_type, "E")
        self.assertEqual(run.exception.msg_number, "107")
        self.assertEqual(run.exception.msg_v1, "V1 text (ABAP_MESSAGE)")

        with self.assertRaises(ExternalRuntimeError) as run:
            test.invoke_srv_function("STFC_CONNECTION", REQUTEXT="FAILURE")
        self.assertEqual(run.exception.code, 15, "rc")
        self.assertEqual(run.exception.message[:9], "Something")

        with self.assertRaises(ExternalRuntimeError) as run:
            test.invoke_srv_function("STFC_CONNECTION", REQUTEXT="INVALID")
        self.assertEqual(run.exception.code, 15, "rc")
        self.assertEqual(run.exception.message[:7], "Invalid")


if __name__ == '__main__':
    unittest.main()

