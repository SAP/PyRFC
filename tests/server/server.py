from pyrfc import Server, set_ini_file_directory

def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked");
    print("request_context", request_context);
    print(f"REQUTEXT: {REQUTEXT}");

    return {
        "ECHOTEXT": REQUTEXT,
        "RESPTEXT": "Python server here"
    }


set_ini_file_directory("/Users/d037732/src/NG-APPS/PyRFC/tests/server")

server = Server({"dest": "gateway"}, {"dest": "MME"})

server.add_function("STFC_CONNECTION", my_stfc_connection )

server.serve(20)

