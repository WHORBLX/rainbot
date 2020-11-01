# Stubs for pymongo.uri_parser (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from bson.py3compat import abc
from typing import Any, Dict, List, Mapping, Optional, Tuple

SCHEME: str = ...
SCHEME_LEN: int = ...
SRV_SCHEME: str = ...
SRV_SCHEME_LEN: int = ...
DEFAULT_PORT: int = ...

def parse_userinfo(userinfo: str) -> Tuple[str, str]: ...
def parse_ipv6_literal_host(entity: str, default_port: int) -> Tuple[str, int]: ...
def parse_host(entity: str, default_port: int = ...) -> Tuple[str, int]: ...
def validate_options(opts: Mapping[str, Any], warn: bool = ...) -> Dict[str, Any]: ...
def split_options(opts: str, validate: bool = ..., warn: bool = ..., normalize: bool = ...) -> Dict[str, Any]: ...
def split_hosts(hosts: str, default_port: Any = ...) -> List[Tuple[str, int]]: ...
def parse_uri(uri: str, default_port: int = ..., validate: bool = ..., warn: bool = ...) -> Dict[str, Any]: ...
