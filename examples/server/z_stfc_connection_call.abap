*&---------------------------------------------------------------------*
*& Report ZSERVERTEST
*&---------------------------------------------------------------------*
*& MME/620
*&---------------------------------------------------------------------*
report zservertest.

data lv_echo like sy-lisel.
data lv_resp like sy-lisel.
data lv_error_message type char512.

do 10 times.

  call function 'STFC_CONNECTION' destination 'NODEJS'
    exporting
      requtext              = 'XYZ'
    importing
      echotext              = lv_echo
      resptext              = lv_resp
    exceptions
      communication_failure = 1 message lv_error_message
      system_failure        = 2 message lv_error_message.

  if sy-subrc = 0.
    write lv_echo.
    write lv_resp.
  else.
    write lv_error_message.
    exit.
  endif.
enddo.