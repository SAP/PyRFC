from pyrfc import Server, Connection, RFCError, RFCLibError, \
                      ABAPApplicationError, ABAPRuntimeError, \
                      ExternalRuntimeError
from pyrfc._pyrfc import _Testing

from ConfigParser import ConfigParser
import sys

config = ConfigParser()
config.read('sapnwrfc.cfg')
params_connection = config._sections['connection']
conn = Connection(**params_connection)
test = _Testing()

# Instantiate server
params_gateway = config._sections['gateway']
# server = Server(config={'debug': True}, **params_gateway)
server = Server(config={'debug': True}, **params_gateway)

# Create callback functions and retrieve correspondent descriptions
#def my_stfc_connection(**kwargs):
#    print "my_stfc_connection was called with arguments: {}".format(kwargs)
#    return {
#        'ECHOTEXT': kwargs['REQUTEXT'],
#        'RESPTEXT': u"Local server here."
#    }
def my_stfc_connection(request_context, REQUTEXT=""):
    #print "my_stfc_connection was called with arguments: {}".format(kwargs)
    return {
        'ECHOTEXT': REQUTEXT,
        'RESPTEXT': u"Local server here."
    }
# func_desc_stfc_connection = conn.get_function_description("STFC_CONNECTION")
# server.install_function(func_desc_stfc_connection, my_stfc_connection)

def my_stfc_changing(request_context, **kwargs): # TODO: Maybe only expect import/changing/tables values.
    print "my_stfc_changing was called with arguments: {}".format(kwargs)
    start_value = kwargs['START_VALUE']
    counter = kwargs['COUNTER']
    return {
        'START_VALUE': start_value,
        'COUNTER': counter + 2,
        'RESULT': start_value + 2*counter
    }
func_desc_stfc_changing = conn.get_function_description("STFC_CHANGING")
server.install_function(func_desc_stfc_changing, my_stfc_changing)

def my_raise_error(request_context, REQUTEXT):
    ERRTYPE = REQUTEXT
    if ERRTYPE == 'EXCEPTION':
        raise ABAPApplicationError(key='BAD_EXCEPTION_HAPPENED')
    elif ERRTYPE == 'EXCEPTION_MESSAGE':
        raise ABAPApplicationError(key='BAD_EXCEPTION_W_MSG',
            msg_class='SR', # message id or class
            msg_type='E', # out of e.g. 'E', 'A' or 'X'
            msg_number='007', # 3 char numeric
            msg_v1='V1 text' # 50 char
        )
    elif ERRTYPE == 'MESSAGE':
        raise ABAPRuntimeError(
            msg_class='SM', # message id or class
            msg_type='E', # out of e.g. 'E', 'A' or 'X'
            msg_number='107', # 3 char numeric string
            msg_v1='V1 text (ABAP_MESSAGE)'
        )
    elif ERRTYPE == 'FAILURE':
        raise ExternalRuntimeError("Something very bad happened.")
    elif ERRTYPE == 'EXCEPTION_TOO_LONG':
        raise ABAPApplicationError(key='ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ')
    elif ERRTYPE == 'INVALID':
        raise RFCError("This is an invalid exception.")
    elif ERRTYPE == 'INVALID2':
        raise RFCLibError("This is an invalid exception.", 23, "INV_EXC")
    return {
        'ECHOTEXT': REQUTEXT,
        'RESPTEXT': u"Local (raise error) server here. Use the following values"
                    u"for REQUTEXT: EXCEPTION, EXCEPTION_MESSAGE, MESSAGE, or"
                    u"FAILURE."
    }
func_desc_stfc_connection = conn.get_function_description("STFC_CONNECTION")
server.install_function(func_desc_stfc_connection, my_raise_error)

#func_desc_serv = conn.test_get_srv_func_desc("STFC_CONNECTION")
#
#print "Function description (retrieved from SAP):"
#print func_desc_stfc_connection.to_string()
#
#print "Function description (retrieved from server):"
#print func_desc_serv.to_string()
#
#print "--- Server test invocation ---"
#
#result = conn.test_invoke_srv_function("STFC_CONNECTION", REQUTEXT="Hola mundo!")
#print "Result is: \n{}".format(result)

if __name__ == '__main__':
    duration = 20
    print "--- Server registration and serving (for {} seconds)---".format(duration)
    server.serve(duration)