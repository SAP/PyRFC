*&---------------------------------------------------------------------*
*& Report ZSERVERTEST
*&---------------------------------------------------------------------*
*& QM7/005
*&---------------------------------------------------------------------*
report zservertest.

data ls_struct like  rfctest.
data lt_table like table of rfctest.
data lv_resp like sy-lisel.
data lv_error_message type char512.

do 10 times.
  add 1 to : ls_struct-RFCINT1, ls_struct-RFCINT2, ls_struct-RFCINT4.
  insert ls_struct into table lt_table.
  call function 'STFC_STRUCTURE' destination 'NODEJS'
    exporting
      importstruct          = ls_struct
    importing
      echostruct            = ls_struct
      resptext              = lv_resp
    tables
      rfctable              = lt_table
    exceptions
      communication_failure = 1 message lv_error_message
      system_failure        = 2 message lv_error_message
      .

  if sy-subrc = 0.
    write lv_resp.
  else.
    write lv_error_message.
    exit.
  endif.

enddo.