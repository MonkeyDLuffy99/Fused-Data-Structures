from __future__ import annotations

from typing import Dict, SupportsIndex, Optional, List

from protos.service_pb2 import StructureType
from servers.observers.console import console_observer
from servers.shared.decorators import emits, observed_by
from servers.shared.events import MutationEvent, RemoveItemEvent, SetItemEvent
from servers.structures.fused.interface import FusedStructure, FusedNode, FusedAuxNode
from shared.types import ClusterInformation


@observed_by(observers=[console_observer])
class FusedMap(FusedStructure):
    def __init__(self, cluster_information: ClusterInformation, backup_code_position: int):
        super().__init__(cluster_information, backup_code_position)
        self.__aux_structure: Dict[str, Dict[SupportsIndex, FusedAuxNode]] = {}
        self.__aux_structure_initialised = False
        self.__structure_type = StructureType.MAP

    def __str__(self) -> str:
        return str(self.__aux_structure)

    def __len__(self) -> int:
        return max(map(len, self.__aux_structure))

    def _initialise_aux_structure(self) -> None:
        if not self.__aux_structure_initialised and self._registration_lock:
            self.__aux_structure = {x: {} for x in self.primary_structure_identifiers}
        self.__aux_structure_initialised = True

    @property
    def structure_type(self):
        return self.__structure_type

    async def process_event(self, event: MutationEvent) -> None:
        self._initialise_aux_structure()

        if isinstance(event, SetItemEvent):
            await self.set(event.index, event.value, event.old_value, event.structure_identifier)

        elif isinstance(event, RemoveItemEvent):
            await self.remove(event.index, event.value, event.value_to_replace_with, event.structure_identifier)

    @emits(SetItemEvent)
    def set(self, key: SupportsIndex, value: int, old_value: Optional[int], primary_structure_identifier: str) -> Dict:
        if key in self.__aux_structure.get(primary_structure_identifier):
            node_to_update: FusedNode = self.__aux_structure.get(primary_structure_identifier)[key].fused_node
            node_to_update.remove_element(old_value, primary_structure_identifier, self.backup_code_position, self.fusion_accessor)
            node_to_update.add_element(value, primary_structure_identifier, self.backup_code_position, self.fusion_accessor)
        else:
            aux_node = self._add(value, primary_structure_identifier)
            self.__aux_structure.get(primary_structure_identifier)[key] = aux_node

        return {"index": key, "value": value, "primaryStructureIdentifier": primary_structure_identifier}

    @emits(RemoveItemEvent)
    def remove(self, key: SupportsIndex, value: int, value_to_replace_with: int, primary_structure_identifier: str) -> Dict:
        aux_node = self.__aux_structure.get(primary_structure_identifier).pop(key)
        self._remove(value, value_to_replace_with, aux_node, primary_structure_identifier)

        return {"index": key, "value": value, "valueToReplaceWith": value_to_replace_with, "primaryStructureIdentifier": primary_structure_identifier}

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
                    aux_structure = self.__aux_structure.get(primary_structure_identifier)
                    key = next((k for k, v in aux_structure.items() if v == aux_node), None)
                    positions.append(key)

            indexes.append(positions)
            node = self._data_stack.get_next(node)

        return indexes
