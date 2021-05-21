from typing import Any, Optional, Dict, TypedDict

class NWRFCSDKVersion(TypedDict):
    major: int
    minor: int
    patchLevel: int
    platform: str

class ClientOptions(TypedDict):
    dtime: bool = False
    return_import_params: bool = False
    rstrip: bool = True

def get_nwrfclib_version() -> NWRFCSDKVersion: ...
def set_ini_file_directory(path_name: str) -> None: ...

class Connection:
    version: NWRFCSDKVersion
    def __init__(
        self,
        config: ClientOptions = {
            "dtime": False,
            "return_import_params": False,
            "rstrip": True,
        },
        **kwargs: str
    ) -> None: ...

__VERSION__: str
