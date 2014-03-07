ReadTable
=========

ReadTable is a helper class to fetch R/3 table data by calling RFC_READ_TABLE over a PyRFC connection.

RFC_READ_TABLE returns an unformatted result set and the data need to be parsed for them to be usable. 
ReadTable parses the results for you and converts values into Python built-in types.


Example usage
-------------

You need create a ReadTable object you pass it a PyRFC connection object and a table name. Then, by calling
instance methods, you can apply filters ("WHERE" clauses) and choose wich columns to retrieve. 

The all() method calls the remote function and returns all matched lines.

The result is a list of ObjectDict objects. 
You can access the values for each line using the column name as a dictionary key or attribute name.

>>> mats = ReadTable(con, 'MARA').fields(['matnr', 'mtart']).filter("mtart = 'FERT'").all()
>>> for mat in mats:
>>>     print mat.matr, mat['matnr']


Retrieving a subset of columns
''''''''''''''''''''''''''''''

If you do not specify which columns to retrieve, the results will contain the values for all the columns
in the table (the same as a SELECT * statement). 

To select a subset of columns, the call the fields() method of the ReadTable object passing a list of the 
names of the columns that you wish to retrieve.

>>> mats = ReadTable(con, 'MARA').fields(['matnr', 'mtart']).all()

.. IMPORTANT::
   If the table has a large number of columns and you select them all, an ABAPApplicationError exception 
   with the key DATA_BUFFER_EXCEEDED might be raised by R/3.
   You will need to specify a subset of all columns to get results.


Retrieving specific objects with filters
'''''''''''''''''''''''''''''''''''''''''

To construct the "WHERE" clause for the table query, call the filter method with the condition as text:

>>> mats = ReadTable(con, 'MARA').filter("mtart = 'FERT'").all()

You can chain multiple filter times and tho refine your query

>>> mats = ReadTable(con, 'MARA').filter("mtart = 'FERT'").filter(" AND ERSDA >= '01.01.2001'").all()

is the same as 

    SELECT * FROM MARA WHERE mtart = 'FERT' AND mtart = 'FERT'

Or you can pass in a more complex condition:

>>> mats = ReadTable(con, 'MARA').filter("mtart = 'FERT' AND ERSDA >= '01.01.2001'").all()


.. IMPORTANT::
    The argument to filter must be a string and have spaces around the comparison operator.



Retrieving a single result with get
'''''''''''''''''''''''''''''''''''

The get() method will only return the first result matched by your query, as a ObjectDict instance:

>>> mat = ReadTable(con, 'MARA').filter("mtart = 'FERT'").get()


Retrieving a portion of the matched rows
''''''''''''''''''''''''''''''''''''''''

The limit() and offset() allow you to retrieve just a portion of the rows matched by the query.

You can use the offset() method to define the first line to fetch:
    
>>> mat = ReadTable(conn,'MARA').offset(4).get()

will return the only 4th result.

The limit() method allows you to define the number of lines fo retrieve:

>>> mat = ReadTable(conn,'MARA').offset(11).limit(10).all()

will return lines 11 to 20.


Data types
----------

ReadTable will convert the results into native Python types in a similar way to the Python connector.

.. table:: Data types

     =========== ===== ============================= ============= ===============================
     Type         ABAP Meaning                       Python         Remarks
     =========== ===== ============================= ============= ===============================
     numeric     I     Integer (whole number)        int            
     numeric     F     Floating point number         float    
     numeric     P     Packed number                 None           Not supported at the moment
     character   C     Text field                    unicode      
     character   D     Date field (Format: YYYYMMDD) datetime.date    
     character   T     Time field (Format: HHMMSS)   datetime.time    
     character   N     Numeric text field            unicode      
     hexadecimal X     Hexadecimal field             str [bytes]      
     =========== ===== ============================= ============= ===============================


Tests:
------

The tests in the test/ directory use the table TRDIR, present on every R/3 system. To run the tests, 
fill in your test configuration settings on the sapnerfc.cfg file in the tests directory.
