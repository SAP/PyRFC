from pyrfc import Server, set_ini_file_directory

def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked");
    print("request_context", request_context);
    print(f"REQUTEXT: {REQUTEXT}");

    return {
        "ECHOTEXT": REQUTEXT,
        "RESPTEXT": "Python server here"
    }

def my_auth_check(func_name=False, request_context = {}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0

set_ini_file_directory("/Users/d037732/src/NG-APPS/PyRFC/tests/server")

server = Server({"dest": "gateway"}, {"dest": "MME"})
# server = Server({"dest": "gateway"}, {"dest": "MME"}, {"auth_check": my_auth_check, "server_log": True})

server.add_function("STFC_CONNECTION", my_stfc_connection )

server.serve(20)

