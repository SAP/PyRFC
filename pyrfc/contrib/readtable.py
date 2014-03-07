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

""" Classes to fetch R/3 table data by calling RFC_READ_TABLE over a PyRFC connection. """

from datetime import date, time


class ReadTable(object):
    """
    This class offers a pythonic interface for reading data from an R/3 table by
    calling RFC_READ_TABLE.
    """
    def __init__(self, con, table):
        """
        con - pyrfc.Connection object to the target system
        table - name of the table to read (string)
        """
        self.con = con
        self.table = table.upper()
        self._options = []
        self._fields = []
        self._rowskips = 0
        self._limit = None

    def filter(self, option):
        """must be a string and have spaces around comparison"""
        assert type(option) == type("")
        self._options.append(option.upper())
        return self

    def fields(self, fldlst):
        """Choose which fields to retrieve.

        fldlst should be a list of field names, or a single field name.
        """
        if type(fldlst) == type([]):
            self._fields = fldlst
        else:
            self._fields = [fldlst]
        return self

    def get(self):
        """Return just one item"""
        res = self.limit(1).all()
        return res[0] if res else None

    def limit(self, limit):
        """How many items to retrieve from the database."""
        self._limit = limit
        return self

    def all(self):
        """
        Return all items (or up to the maximum defined, if limit() was called
        before) matched by the query
        """
        fields = [{'FIELDNAME': name.upper()} for name in self._fields]
        options = [{'TEXT': opt} for opt in self._options]
        inputs = {'QUERY_TABLE':self.table, 'OPTIONS':options, 'FIELDS':fields}
        if self._limit is not None:
            inputs['ROWCOUNT'] = self._limit
        if self._rowskips:
            inputs['ROWSKIPS'] = self._rowskips
        res = self.con.call('RFC_READ_TABLE', **inputs)
        return self.convert_output(res)

    def convert_date(self, value):
        """convert from YYYYMMDD string"""
        return date(int(value[:4]), int(value[4:6]), int(value[6:]))

    def convert_time(self, value):
        """convert from HHMMSS"""
        return time(int(value[:2]), int(value[2:4]), int(value[4:6]))

    def convert_output(self, data):
        """
        Convert the data returned by the remote call to a list of ObjectDict objects,
        also converting column values to native python types.
        """
        res = []
        fields = data['FIELDS']
        for row in data['DATA']:
            itm = {}
            rawdata = row['WA']
            for fld in fields:
                start, slen = int(fld['OFFSET']), int(fld['LENGTH'])
                fld_type = fld['TYPE']
                value = rawdata[start:(start+slen)]
                if fld_type == 'P':
                    value = None  # Doesn't seem supported by RFC_READ_TABLE (value)
                    # Or raise exception
                elif fld_type == 'F':
                    value = float(value)
                elif fld_type == 'I':
                    value = int(value)
                elif fld_type == 'D':
                    if value == '00000000':
                        value = None
                    else:
                        value = self.convert_date(value)
                elif fld_type == 'T':
                    if value == '      ':
                        value = None
                    else:
                        value = self.convert_time(value)
                elif fld_type == 'X':
                    value = value.decode('hex')
                else:
                    value = value.strip()
                itm[fld['FIELDNAME'].lower()] = value
            res.append(ObjectDict(itm))
        return res

    def offset(self, n):
        """Result to start at position n"""
        self._rowskips = n - 1
        return self


class ObjectDict(dict):
    """ Dictionary that also has object access to attributes """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


