from pyrfc import ABAPRuntimeError

errorInfo = {
    "code": 4,
    "key": "Function not supported",
    "message": "",
    "msg_class": "SR",
    "msg_type": "A",
    "msg_number": "006",
    "msg_v1": "",
    "msg_v2": "",
    "msg_v3": "",
    "msg_v4": "",
}

err = ABAPRuntimeError(**errorInfo)

print(err)
