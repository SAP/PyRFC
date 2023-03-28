*&---------------------------------------------------------------------*
*& Report   z_nwrfc_server_bgrfc
*&
*&---------------------------------------------------------------------*
*&
*&
*&---------------------------------------------------------------------*

report  z_nwrfc_server_bgrfc.

type-pools: abap.


parameters:
  qname_o  type qrfc_queue_name default 'BASIS_BGRFC_OUTIN', "#EC *
  qname_in type qrfc_queue_name default 'RFCSDK_BGRFC_OUTIN', "#EC *
  rfcdest  type rfcdes-rfcdest default 'NWRFC_SERVER_OS',   "#EC *
  n_unit   type syindex default 1,                          "#EC *
  n_call   type syindex default 1,                          "#EC *
  lock_out type abap_bool default abap_false,               "#EC *
  lock_in  type abap_bool default abap_true,                "#EC *
  updtask  type abap_bool default abap_false,               "#EC *
  upd_loc  type abap_bool default abap_false.               "#EC *

constants:
  lc_no_of_data_lines type i value 1,
  lc_unit_data        type txline  value '12345678901234567890123456789012'.

data:
  l_queue_name   type qrfc_queue_name,
  lt_queue_names type qrfc_queue_name_tab,
  l_unit_count   type syindex,
  lt_tcpic       type standard table of abaptext.

data:
  l_dest type ref to if_bgrfc_destination_outbound,
  l_unit type ref to if_qrfc_unit_outinbound.

data:
  l_lock_id_outbound  type bgrfc_lock_id.                   "#EC NEEDED


l_queue_name = qname_o.


write: / text-003, 25 qname_o.
write: / text-004, 25 qname_in.
write: / text-005, 25 rfcdest.

start-of-selection.
* Fill TCPICDAT as required
  perform fill_tcpic_tab using    lc_no_of_data_lines
                                  l_queue_name
                                  lc_unit_data
                         changing lt_tcpic.

* Create the destination object references
  try.
      l_dest = cl_bgrfc_destination_outbound=>create( rfcdest ).
    catch cx_bgrfc_invalid_destination.
      message e103(bgrfc) with rfcdest.

  endtry.

  do n_unit times.
    skip 1.

*   Activate local update task
    if upd_loc = abap_true.
      set update task local.
    endif.

*   Create new qRFC out-inbound unit
    l_unit = l_dest->create_qrfc_unit_outinbound( ).

*    Lock unit on Outbound and/or Inbound side
    if lock_out <> abap_false.
      l_lock_id_outbound = l_unit->lock( ).
    endif.

    if lock_in <> abap_false.
      l_unit->lock_at_inbound( ).
    endif.

*   Assign the unit to a queue
*   Outbound qname
    insert qname_o  into table lt_queue_names.
    l_unit->add_queue_names_outbound( queue_names = lt_queue_names ).
*   Inbound qname
    clear lt_queue_names.
    insert qname_in into table lt_queue_names.
    l_unit->add_queue_names_inbound( queue_names = lt_queue_names ).

*   Using UPDATE TASK, called once per unit
    if ( abap_true = updtask ).
      call function 'CALL_V1_PING' in update task.
    endif.

*   Output
    l_unit_count = sy-index.
    write: / text-001, 30 l_unit_count.
    write: / text-002, 30 n_call.

    do n_call times.

      call function 'STFC_WRITE_TO_TCPIC'
        in background unit l_unit
        tables
          tcpicdat = lt_tcpic.

    enddo.
    commit work.
  enddo.

* Additional information
  skip 1.
  if lock_out <> abap_false.
    write: /'Outbound-Unit lock set!'.                      "#EC NOTEXT
  endif.

  if lock_in <> abap_false.
    write: /'Inbound-Unit lock set!'.                       "#EC NOTEXT
  endif.

  if ( abap_true = updtask ).
    write: /'Unit called together with update task!'.       "#EC NOTEXT
  endif.


*&--------------------------------------------------------------------*
*&      Form  FILL_TCPIC_TAB
*&--------------------------------------------------------------------*
*       text
*---------------------------------------------------------------------*
*      -->l_no_of_data_lines  text
*      -->l_queue_name        text
*      -->l_unit_data         text
*      -->lt_tcpic            text
*---------------------------------------------------------------------*
form fill_tcpic_tab using    l_no_of_data_lines type i
                             l_queue_name       type qrfc_queue_name
                             l_unit_data        type txline
                    changing lt_tcpic           type index table.

  data:
    l_tcpic      type abaptext,
    l_line_nr(5) type n value 0.

  if ( 0 = l_no_of_data_lines ).
    return.
  endif.

  clear lt_tcpic.

  l_tcpic = l_queue_name.
  l_tcpic+40(32) = l_unit_data.

  do l_no_of_data_lines times.
    add 1 to l_line_nr.
    l_tcpic+20(6) = l_line_nr.

    append l_tcpic to lt_tcpic.

  enddo.

endform.                    "FILL_TCPIC_TAB