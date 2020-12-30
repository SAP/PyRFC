
from typing import Any, Optional, Dict
def get_nwrfclib_version(): tuple
def set_ini_file_directory(path_name: str): None

class Connection():
    version: {major: int, minor: int, patchLevel: int}
    def __init__(self, config: Optional[Dict] = {}, *params: Any) -> None: ...

__VERSION__: str
