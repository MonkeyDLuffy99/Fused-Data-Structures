from __future__ import annotations

from typing import List, Dict, Optional

from protos.service_pb2 import StructureType
from servers.observers.console import console_observer
from servers.shared.decorators import emits, observed_by
from servers.shared.events import MutationEvent, RemoveItemEvent, SetItemEvent
from servers.structures.fused.interface import FusedStructure, FusedAuxNode, FusedNode
from shared.types import ClusterInformation


@observed_by(observers=[console_observer])
class FusedList(FusedStructure):
    def __init__(self, cluster_information: ClusterInformation, backup_code_position: int):
        super().__init__(cluster_information, backup_code_position)
        self.__aux_structure: Dict[str, List[FusedAuxNode]] = {}
        self.__aux_structure_initialised = False
        self.__structure_type = StructureType.LIST

    def __str__(self) -> str:
        return str(self.__aux_structure)

    def __len__(self) -> int:
        return max(map(len, self.__aux_structure))

    def _initialise_aux_structure(self) -> None:
        if not self.__aux_structure_initialised and self._registration_lock:
            self.__aux_structure = {x: [] for x in self.primary_structure_identifiers}
        self.__aux_structure_initialised = True

    @property
    def structure_type(self):
        return self.__structure_type

    async def process_event(self, event: MutationEvent) -> None:
        self._initialise_aux_structure()

        if isinstance(event, SetItemEvent):
            await self.add(int(event.index), event.value, event.structure_identifier)

        elif isinstance(event, RemoveItemEvent):
            await self.remove(int(event.index), event.value, event.value_to_replace_with, event.structure_identifier)

    @emits(SetItemEvent)
    def add(self, index: int, value: int, primary_structure_identifier: str) -> Dict:
        aux_node = self._add(value, primary_structure_identifier)
        self.__aux_structure.get(primary_structure_identifier).insert(index, aux_node)

        return {"index": index, "value": value, "primaryStructureIdentifier": primary_structure_identifier}

    @emits(RemoveItemEvent)
    def remove(self, index: int, value: int, value_to_replace_with: int, primary_structure_identifier: str) -> Dict:
        aux_node = self.__aux_structure.get(primary_structure_identifier).pop(index)
        self._remove(value, value_to_replace_with, aux_node, primary_structure_identifier)

        return {"index": index, "value": value, "valueToReplaceWith": value_to_replace_with, "primaryStructureIdentifier": primary_structure_identifier}

    def get_index_data(self) -> List[List[int]]:
        indexes: List[List[int]] = []

        node: Optional[FusedNode] = self._data_stack.get_first()
        while node is not None:
            positions = []
            for primary_structure_identifier in self.primary_structure_identifiers:
                aux_node: Optional[FusedAuxNode] = node.aux_nodes[primary_structure_identifier]
                if aux_node is None:
                    positions.append(-1)
                else:
                    positions.append(self.__aux_structure.get(primary_structure_identifier).index(aux_node))

            indexes.append(positions)
            node = self._data_stack.get_next(node)

        return indexes
