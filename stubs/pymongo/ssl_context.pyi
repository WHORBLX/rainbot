from socket import socket
from typing import Any, Optional

try:
    import ssl
except ImportError:
    pass


class SSLContext(object):
    def __init__(self, protocol: int) -> None: ...
    @property
    def protocol(self) -> int: ...
    def __get_verify_mode(self) -> int: ...
    def __set_verify_mode(self, value: int) -> None: ...
    def load_cert_chain(self, certfile: str, keyfile: Optional[str] = ...) -> None: ...
    def load_verify_locations(self, cafile: Optional[str] = ..., dummy: Optional[Any] = ...) -> None: ...
    def wrap_socket(
        self,
        sock: socket,
        server_side: bool = ...,
        do_handshake_on_connect: bool = ...,
        suppress_ragged_eofs: bool = ...,
        dummy: Optional[Any] = ...) -> ssl.SSLSocket: ...
