# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an.
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific.
# language governing permissions and limitations under the License.

from ConfigParser import ConfigParser
import datetime
import os
import unittest
import pyrfc
from pyrfc.contrib.readtable import ReadTable

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'sapnwrfc.cfg'))


class ReadTableTest(unittest.TestCase):
    """Tests over a real connection to an R/3 system"""
    def setUp(self):
        self.con = pyrfc.Connection(**config._sections['connection'])

    def test_view_single(self):
        """Check the basic call works over a real RFC"""
        res = ReadTable(self.con, 'TRDIR').fields(['name', 'cnam', 'subc']).filter("name = 'BCALV_GRID_01'").get()
        self.assertEqual(res.name, 'BCALV_GRID_01')
        self.assertEqual(res.cnam, 'SAP')
        self.assertEqual(res.subc, '1')

    def test_limit(self):
        """Check that limiting the number of records works"""
        res = ReadTable(self.con, 'TRDIR').fields(['name', 'cnam', 'subc']).limit(10).all()
        self.assertEqual(len(res), 10)

    def test_offset(self):
        """Check that setting the start record works"""
        res = ReadTable(self.con, 'TRDIR').fields(['name', 'cnam', 'subc']).limit(5).all()
        expected = res[4]
        res = ReadTable(self.con, 'TRDIR').fields(['name', 'cnam', 'subc']).offset(5).get()
        self.assertEqual(res, expected)


class DataConversionTest(unittest.TestCase):
    """Unit tests for ReadTable methods"""
    def test_datatypes(self):
        """Test datatype conversion."""
        rt = ReadTable(None, 'NO_TABLE')
        data = {u'FIELDS': [{u'FIELDTEXT': u'Material Number', u'TYPE': u'C', u'LENGTH': u'000018', u'FIELDNAME': u'TEXT_FIELD', u'OFFSET': u'000000'}, {u'FIELDTEXT': u'Page Number of Part', u'TYPE': u'I', u'LENGTH': u'000010', u'FIELDNAME': u'INT_FIELD', u'OFFSET': u'000018'}, {u'FIELDTEXT': u'Field of type FLTP', u'TYPE': u'F', u'LENGTH': u'000016', u'FIELDNAME': u'FLOAT_FIELD', u'OFFSET': u'000028'}, {u'FIELDTEXT': u'Beta Factor (Trend Value Smoothing)', u'TYPE': u'P', u'LENGTH': u'000003', u'FIELDNAME': u'PACKED_FIELD', u'OFFSET': u'000044'}, {u'FIELDTEXT': u'Date', u'TYPE': u'D', u'LENGTH': u'000008', u'FIELDNAME': u'DATE_FIELD', u'OFFSET': u'000047'}, {u'FIELDTEXT': u'Serial Number', u'TYPE': u'N', u'LENGTH': u'000018', u'FIELDNAME': u'NUMTEXT_FIELD', u'OFFSET': u'000055'}, {u'FIELDTEXT': u'Time', u'TYPE': u'T', u'LENGTH': u'000006', u'FIELDNAME': u'TIME_FIELD', u'OFFSET': u'000073'}, {u'FIELDTEXT': u'GUID16', u'TYPE': u'X', u'LENGTH': u'000016', u'FIELDNAME': u'HEX_FIELD', u'OFFSET': u'000079'}], u'DATA': [{u'WA': u'XPTO                      1  2.234000000E+01*212013010100002738278937128903002334987CBEEB468BFE'}], u'OPTIONS': []}
        res = rt.convert_output(data)[0]
        self.assertEqual(res['float_field'], 22.34)
        self.assertEqual(res['packed_field'], None)
        self.assertEqual(res['int_field'], 1)
        self.assertEqual(res['numtext_field'], u'000027382789371289')
        self.assertEqual(res['time_field'], datetime.time(3, 0, 23))
        self.assertEqual(res['date_field'], datetime.date(2013, 1, 1))
        self.assertEqual(res['text_field'], u'XPTO')
        self.assertEqual(res['hex_field'], '4\x98|\xbe\xebF\x8b\xfe')

    def test_empty_values(self):
        """Test reading a row with no data (initial values)"""
        rt = ReadTable(None, 'NO_TABLE')
        data = {u'FIELDS': [{u'FIELDTEXT': u'Material Number', u'TYPE': u'C', u'LENGTH': u'000018', u'FIELDNAME': u'TEXT_FIELD', u'OFFSET': u'000000'}, {u'FIELDTEXT': u'Page Number of Part', u'TYPE': u'I', u'LENGTH': u'000010', u'FIELDNAME': u'INT_FIELD', u'OFFSET': u'000018'}, {u'FIELDTEXT': u'Field of type FLTP', u'TYPE': u'F', u'LENGTH': u'000016', u'FIELDNAME': u'FLOAT_FIELD', u'OFFSET': u'000028'}, {u'FIELDTEXT': u'Beta Factor (Trend Value Smoothing)', u'TYPE': u'P', u'LENGTH': u'000003', u'FIELDNAME': u'PACKED_FIELD', u'OFFSET': u'000044'}, {u'FIELDTEXT': u'Date', u'TYPE': u'D', u'LENGTH': u'000008', u'FIELDNAME': u'DATE_FIELD', u'OFFSET': u'000047'}, {u'FIELDTEXT': u'Serial Number', u'TYPE': u'N', u'LENGTH': u'000018', u'FIELDNAME': u'NUMTEXT_FIELD', u'OFFSET': u'000055'}, {u'FIELDTEXT': u'Time', u'TYPE': u'T', u'LENGTH': u'000006', u'FIELDNAME': u'TIME_FIELD', u'OFFSET': u'000073'}, {u'FIELDTEXT': u'GUID16', u'TYPE': u'X', u'LENGTH': u'000016', u'FIELDNAME': u'HEX_FIELD', u'OFFSET': u'000079'}], u'DATA': [{u'WA': u'                          0  0.000000000E+00.0000000000000000000000000000      0000000000000000'}], u'OPTIONS': []}
        res = rt.convert_output(data)[0]
        self.assertEqual(res['float_field'], 0.0)
        self.assertEqual(res['packed_field'], None)
        self.assertEqual(res['int_field'], 0)
        self.assertEqual(res['numtext_field'], u'000000000000000000')
        self.assertEqual(res['time_field'], None)
        self.assertEqual(res['date_field'], None)
        self.assertEqual(res['text_field'], u'')
        self.assertEqual(res['hex_field'], '\x00\x00\x00\x00\x00\x00\x00\x00')



if __name__ == '__main__':
    unittest.main()

