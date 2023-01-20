from __future__ import annotations

from typing import Dict, SupportsIndex, List

from protos.service_pb2 import StructureType
from servers.observers.backup import backup_observer
from servers.observers.console import console_observer
from servers.shared.decorators import emits, observed_by, self_await
from servers.shared.events import MutationEvent, RemoveItemEvent, SetItemEvent
from servers.structures.primary.interface import PrimaryStructure, PrimaryNode
from shared.types import ClusterInformation


@observed_by(observers=[console_observer], async_observers=[backup_observer])
class PrimaryMap(PrimaryStructure):
    def __init__(self, cluster_information: ClusterInformation, backup_ports: List[int]):
        super().__init__(cluster_information, backup_ports)
        self.__items: Dict[SupportsIndex, PrimaryNode] = {}
        self.__structure_type = StructureType.MAP

    def __str__(self) -> str:
        return str(self.__items)

    def __getitem__(self, key) -> PrimaryNode:
        return self.__items[key]

    async def create_backup_connections(self) -> None:
        await self._create_backup_connections(structure_type=self.__structure_type)

    @property
    def values_as_map(self) -> Dict[SupportsIndex, int]:
        values = {}

        for index, value in self.__items.items():
            values[index] = value.value

        return values

    @property
    def structure_type(self):
        return self.__structure_type

    async def process_event(self, event: MutationEvent) -> None:
        if isinstance(event, SetItemEvent):
            await self.set(int(event.index), event.value)

        elif isinstance(event, RemoveItemEvent):
            await self.remove(int(event.index))

    @self_await
    @emits(SetItemEvent)
    def set(self, key: int, value: int) -> Dict:
        old_value = None
        if key in self.__items:
            primary_node = self.__items[key]
            old_value = primary_node.value
            primary_node.value = value
        else:
            primary_node = self._add(value)
            self.__items[key] = primary_node
        return {"index": key, "value": value, "oldValue": old_value}

    @self_await
    @emits(RemoveItemEvent)
    def remove(self, key: int) -> Dict:
        if key not in self.__items:
            raise Exception("Key not in map")

        primary_node = self.__items.pop(key)
        replaced_node = self._remove(primary_node)

        return {"index": key, "nodeToReplaceWith": replaced_node.value}
