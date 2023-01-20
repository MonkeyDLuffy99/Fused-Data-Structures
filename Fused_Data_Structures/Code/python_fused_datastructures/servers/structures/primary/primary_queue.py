from __future__ import annotations

from collections import deque
from typing import List, Dict, Deque

from protos.service_pb2 import StructureType
from servers.observers.backup import backup_observer
from servers.observers.console import console_observer
from servers.shared.decorators import emits, observed_by, self_await
from servers.shared.events import MutationEvent, RemoveItemEvent, SetItemEvent
from servers.structures.primary.interface import PrimaryStructure, PrimaryNode
from shared.types import ClusterInformation


@observed_by(observers=[console_observer], async_observers=[backup_observer])
class PrimaryQueue(PrimaryStructure):
    def __init__(self, cluster_information: ClusterInformation, backup_ports: List[int]):
        super().__init__(cluster_information, backup_ports)
        self.__queue: Deque[PrimaryNode] = deque()
        self.__structure_type = StructureType.QUEUE

    def __str__(self) -> str:
        return str(self.__queue)

    def __len__(self) -> int:
        return len(self.__queue)

    def __getitem__(self, key) -> PrimaryNode:
        return self.__queue[key]

    def __iter__(self) -> PrimaryQueue:
        self.__iteration_position = 0
        return self

    def __next__(self) -> PrimaryNode:
        if self.__iteration_position >= len(self.__items):
            raise StopIteration

        self.__iteration_position += 1
        return self.__queue[self.__iteration_position - 1]

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
            await self.enqueue(event.value)

        elif isinstance(event, RemoveItemEvent):
            await self.dequeue()

    @self_await
    @emits(SetItemEvent)
    def enqueue(self, value: int) -> Dict:
        primary_node = self._add(value)
        self.__queue.append(primary_node)
        insert_index = len(self.__queue) - 1
        return {"index": insert_index, "value": value}

    @self_await
    @emits(RemoveItemEvent)
    def dequeue(self) -> Dict:
        if len(self.__queue) == 0:
            raise Exception("Queue is empty")

        index = 0
        primary_node = self.__queue.popleft()

        replaced_node = self._remove(primary_node)

        return {"index": index, "value": primary_node.value, "valueToReplaceWith": replaced_node.value}
