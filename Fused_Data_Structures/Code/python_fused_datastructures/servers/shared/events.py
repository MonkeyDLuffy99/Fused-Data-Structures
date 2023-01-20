from dataclasses import dataclass
from typing import Callable, Dict, Type, Union, SupportsIndex, Optional, Awaitable

from protos.service_pb2 import StructureType
from servers.backup.connection_manager import BackupStructureConnectionManager


@dataclass
class BaseEvent:
    structure_identifier: str
    cluster_identifier: str
    structure_type: StructureType
    backup_connection_manager: Optional[BackupStructureConnectionManager] = None
    primary_structure_id: Optional[str] = None


class SetItemEvent(BaseEvent):
    def __init__(
        self,
        payload: Dict,
        cluster_identifier: str,
        structure_identifier: str,
        structure_type: StructureType,
        backup_connection_manager: Optional[BackupStructureConnectionManager] = None
    ) -> None:
        self.index: SupportsIndex = payload["index"]
        self.value: int = payload["value"]

        # Only present when sending message to fused node from a map
        self.old_value: Optional[int] = payload.get("oldValue")

        primary_structure_identifier = payload.get("primaryStructureIdentifier")
        super().__init__(structure_identifier, cluster_identifier, structure_type, backup_connection_manager, primary_structure_identifier)


class RemoveItemEvent(BaseEvent):
    def __init__(
        self,
        payload: Dict,
        cluster_identifier: str,
        structure_identifier: str,
        structure_type: StructureType,
        backup_connection_manager: Optional[BackupStructureConnectionManager] = None
    ) -> None:
        self.index: SupportsIndex = payload["index"]

        # Only present when sending message to fused node
        self.value: Optional[int] = payload.get("value")
        self.value_to_replace_with = payload.get("valueToReplaceWith")

        primary_structure_identifier = payload.get("primaryStructureIdentifier")
        super().__init__(structure_identifier, cluster_identifier, structure_type, backup_connection_manager, primary_structure_identifier)


MutationEvent = Union[SetItemEvent, RemoveItemEvent]
MutationEventType = Union[Type[SetItemEvent], Type[RemoveItemEvent]]
MutationEventObserver = Callable[[MutationEvent], None]
MutationEventAsyncObserver = Callable[[MutationEvent], Awaitable]
