from __future__ import annotations

from typing import List, Dict

from protos.service_pb2 import StructureType
from servers.observers.backup import backup_observer
from servers.observers.console import console_observer
from servers.shared.decorators import emits, observed_by, self_await
from servers.shared.events import MutationEvent, RemoveItemEvent, SetItemEvent
from servers.structures.primary.interface import PrimaryStructure, PrimaryNode
from shared.types import ClusterInformation


@observed_by(observers=[console_observer], async_observers=[backup_observer])
class PrimaryList(PrimaryStructure):
    def __init__(self, cluster_information: ClusterInformation, backup_ports: List[int]):
        super().__init__(cluster_information, backup_ports)
        self.__items: List[PrimaryNode] = []
        self.__structure_type = StructureType.LIST

    def __str__(self) -> str:
        return str(self.__items)

    def __len__(self) -> int:
        return len(self.__items)

    def __getitem__(self, key) -> PrimaryNode:
        return self.__items[key]

    def __iter__(self) -> PrimaryList:
        self.__iteration_position = 0
        return self

    def __next__(self) -> PrimaryNode:
        if self.__iteration_position >= len(self.__items):
            raise StopIteration

        self.__iteration_position += 1
        return self.__items[self.__iteration_position - 1]

    def __repr__(self):
        return [x.__repr__() for x in self.__items]

    async def create_backup_connections(self) -> None:
        await self._create_backup_connections(structure_type=self.__structure_type)

    @property
    def values_as_map(self) -> Dict[int, int]:
        values = {}

        for index, value in enumerate(self.__items):
            values[index] = value.value

        return values

    @property
    def structure_type(self):
        return self.__structure_type

    async def process_event(self, event: MutationEvent) -> None:
        if isinstance(event, SetItemEvent):
            await self.add(int(event.index), event.value)

        elif isinstance(event, RemoveItemEvent):
            await self.remove(int(event.index))

    @self_await
    @emits(SetItemEvent)
    def append(self, value: int) -> Dict:
        primary_node = self._add(value)
        self.__items.append(primary_node)
        return {"index": len(self.__items) - 1, "value": value}

    @self_await
    @emits(SetItemEvent)
    def add(self, index: int, value: int) -> Dict:
        primary_node = self._add(value)
        self.__items.insert(index, primary_node)
        return {"index": index, "value": value}

    @self_await
    @emits(RemoveItemEvent)
    def remove(self, index: int) -> Dict:
        if index < 0 or index >= len(self.__items):
            raise Exception("List index out of range")

        primary_node = self.__items.pop(index)
        replaced_node = self._remove(primary_node)

        return {"index": index, "value": primary_node.value, "valueToReplaceWith": replaced_node.value}
