import datetime
from typing import Any, Dict, Optional, Set, Tuple

from pymongo.ismaster import IsMaster
from pymongo.server_type import SERVER_TYPE as SERVER_TYPE


class ServerDescription(object):
    def __init__(
        self,
        address: Tuple[str, int],
        ismaster: Optional[IsMaster] = ...,
        round_trip_time: Optional[float] = ...,
        error: Optional[Any] = ...) -> None: ...
    @property
    def address(self) -> Tuple[str, int]: ...
    @property
    def server_type(self) -> int: ...
    @property
    def server_type_name(self) -> str: ...
    @property
    def all_hosts(self) -> Set[Tuple[str, int]]: ...
    @property
    def tags(self) -> Dict[Any, Any]: ...
    @property
    def replica_set_name(self) -> Optional[str]: ...
    @property
    def primary(self) -> Optional[Tuple[str, int]]: ...
    @property
    def max_bson_size(self) -> int: ...
    @property
    def max_message_size(self) -> int: ...
    @property
    def max_write_batch_size(self) -> int: ...
    @property
    def min_wire_version(self) -> int: ...
    @property
    def max_wire_version(self) -> int: ...
    @property
    def set_version(self) -> int: ...
    @property
    def election_id(self) -> int: ...
    @property
    def election_tuple(self) -> Tuple[int, int]: ...
    @property
    def me(self) -> Tuple[str, int]: ...
    @property
    def last_write_date(self) -> Dict[Any, Any]: ...
    @property
    def last_update_time(self) -> float: ...
    @property
    def round_trip_time(self) -> float: ...
    @property
    def error(self) -> Any: ...
    @property
    def is_writable(self) -> bool: ...
    @property
    def is_readable(self) -> bool: ...
    @property
    def is_server_type_known(self) -> bool: ...
