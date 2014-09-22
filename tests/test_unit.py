#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, pyrfc, unittest, socket, timeit
from ConfigParser import ConfigParser

config = configparser()
config.read('pyrfc.cfg')


class TransactionTest(unittest.TestCase):
    """
    This test cases cover selected functions from the MRFC function group.
    """

    @classmethod
    def setUpClass(cls):
        cls.conn = pyrfc.Connection(**config._sections['connection'])

    @classmethod
    def tearDownClass(cls):
        pass

    def test_id_generation(self):
        unit1 = self.conn.initialize_unit()
        unit2 = self.conn.initialize_unit()
        self.assertEqual(len(unit1['id']), 32)
        self.assertEqual(len(unit2['id']), 32)
        self.assertNotEqual(unit1['id'], unit2['id'])
        # non background units
        unit1 = self.conn.initialize_unit(background=False)
        unit2 = self.conn.initialize_unit(background=False)
        self.assertEqual(len(unit1['id']), 24)
        self.assertEqual(len(unit2['id']), 24)
        self.assertNotEqual(unit1['id'], unit2['id'])

    def _get_idoc_desc(self, idoc_id):
        """ Returns an IDOC description for calling IDOC_INBOUND_ASYNCHRONOUS

        :param idoc_id: Integer value for filling the data records.
        :type idoc: int
        """
        idoc_control = {
            u"TABNAM": u"EDI_DC40",
            u"MANDT": u"000",
            u"DOCNUM": u"{0:016d}".format(idoc_id),
            u"DIRECT": u"2",
            u"IDOCTYP": u"TXTRAW01",
            u"MESTYP": u"TXTRAW",
            u"SNDPRT": u"LS",
            u"SNDPRN": u"SPJ_DEMO",
            u"RCVPRT": u"LS",
            u"RCVPRN": u"T90CLNT090",
            }
        idoc_data_dicts = []
        for i in range(1, idoc_id+2):
            idoc_data = {
                u"SEGNAM": u"E1TXTRW",
                u"MANDT": u"000",
                u"DOCNUM": u"{0:016d}".format(idoc_id),
                u"SEGNUM": u"{0:06d}".format(i),
                u"SDATA": u"El perro de San Roque {}".format(idoc_id + i)
            }
            idoc_data_dicts.append(idoc_data)
        return {
            u"IDOC_CONTROL_REC_40": [idoc_control],
            u"IDOC_DATA_REC_40": idoc_data_dicts
        }


    def test_tRFC_create(self):
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA (base condition).")

        # incomplete parameters
        unit = self.conn.initialize_unit(background=False)
        with self.assertRaises(TypeError) as e:
            self.conn.fill_and_submit_unit(unit)
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA after create-call w/ incomplete params.")

        with self.assertRaises(ValueError) as e:
            self.conn.fill_and_submit_unit(unit, "testtest")
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA after create-call w/ invalid params.")

        # default behavior
        idoc = self._get_idoc_desc(11)
        self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
        self.assertTrue(self.conn.get_connection_attributes()['active_unit'])
        self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
        self.conn.destroy_unit(unit)
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'])

    def test_qRFC_create(self):
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA (base condition).")

        # invalid parameters (more than one queue name given)
        idoc = self._get_idoc_desc(21)
        unit = self.conn.initialize_unit(background=False)
        with self.assertRaises(pyrfc.RFCError) as e:
            self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)], queue_names=['bla', 'fasel'])
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA after create-call w/ invalid params.")

    def test_tbgRFC_create(self):
        pass
        # TODO: implement

    def test_qbgRFC_create(self):
        pass
        # TODO: implement

    def test_unit_get_state(self):
        pass
        # TODO: to implement

    def test_unit_confirm(self):
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA (base condition).")

        unit = self.conn.initialize_unit(background=False)
        with self.assertRaises(pyrfc.RFCError) as e: # missing transaction
            self.conn.confirm_unit(unit)
        self.assertEqual(e.exception.message, u"No transaction handle for this connection available.")

        unit = self.conn.initialize_unit(background=False)
        idoc = self._get_idoc_desc(31)
        with self.assertRaises(pyrfc.RFCError) as e: # already destroyed transaction
            self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
            self.conn.destroy_unit(unit)
            self.conn.confirm_unit(unit)
        self.assertEqual(e.exception.message, u"No transaction handle for this connection available.")

        unit = self.conn.initialize_unit(background=False)
        idoc = self._get_idoc_desc(32)
        with self.assertRaises(pyrfc.RFCError) as e: # already confirmed transaction
            self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
            self.conn.confirm_unit(unit)
            self.conn.confirm_unit(unit)
        self.assertEqual(e.exception.message, u"No transaction handle for this connection available.")

    def test_unit_destroy(self):
        self.assertFalse(self.conn.get_connection_attributes()['active_unit'], u"No active TA (base condition).")

        unit = self.conn.initialize_unit(background=False)
        with self.assertRaises(pyrfc.RFCError) as e: # missing transaction
            self.conn.destroy_unit(unit)
        self.assertEqual(e.exception.message, u"No transaction handle for this connection available.")

        unit = self.conn.initialize_unit(background=False)
        idoc = self._get_idoc_desc(41)
        with self.assertRaises(pyrfc.RFCError) as e: # already destroyed transaction
            self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
            self.conn.destroy_unit(unit)
            self.conn.destroy_unit(unit)
        self.assertEqual(e.exception.message, u"No transaction handle for this connection available.")

        unit = self.conn.initialize_unit(background=False)
        idoc = self._get_idoc_desc(42)
        with self.assertRaises(pyrfc.RFCError) as e: # already confirmed transaction
            self.conn.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
            self.conn.confirm_unit(unit)
            self.conn.destroy_unit(unit)
        self.assertEqual(e.exception.message, u"No transaction handle for this connection available.")

if __name__ == '__main__':
    unittest.main()

