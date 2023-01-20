from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List

from protos.service_pb2 import StructureType
from servers.structures.generic.doubly_linked_list import DoublyLinkedNode, DoublyLinkedList
from servers.structures.interface import Structure

from uuid import uuid4

from shared.types import ClusterInformation
from shared.fusion import FusionAccessor


class FusedNode(DoublyLinkedNode):
    """Store of information in the fused structure"""

    def __init__(self, primary_structure_identifiers: List[str]) -> None:
        super().__init__()
        self.__identifier = str(uuid4())
        self.__primary_structure_identifiers = primary_structure_identifiers
        self.__encoded_data = 0
        self.aux_nodes: Dict[str, Optional[FusedAuxNode]] = {x: None for x in primary_structure_identifiers}
        self.__ref_count = 0

    def __repr__(self):
        return self.__identifier

    def add_element(
        self,
        new_element,
        primary_structure_identifier: str,
        backup_code_position: int,
        fusion_accessor: FusionAccessor
    ) -> None:
        primary_structure_position = self.__primary_structure_identifiers.index(primary_structure_identifier)

        self.__encoded_data = fusion_accessor.get_updated_code(
            self.__encoded_data or 0,
            backup_code_position,
            0,
            int(new_element),
            primary_structure_position
        )

        self.__ref_count += 1

    def remove_element(
        self,
        old_element,
        primary_structure_identifier: str,
        backup_code_position: int,
        fusion_accessor: FusionAccessor
    ) -> None:
        primary_structure_position = self.__primary_structure_identifiers.index(primary_structure_identifier)

        self.__encoded_data = fusion_accessor.get_updated_code(
            self.__encoded_data or 0,
            backup_code_position,
            int(old_element),
            0,
            primary_structure_position
        )

        self.__ref_count -= 1

    def is_empty(self) -> bool:
        return self.__ref_count == 0

    @property
    def encoded_data(self) -> int:
        return self.__encoded_data


@dataclass
class FusedAuxNode:
    fused_node: FusedNode


class FusedStructure(Structure, ABC):
    def __init__(self, cluster_information: ClusterInformation, backup_code_position: int):
        super().__init__(cluster_information)
        self.primary_structure_identifiers: List[str] = []
        self._registration_lock = False
        self.__data_stack = DoublyLinkedList[FusedNode]()
        self.__fused_node_top_of_stack: Dict[str, Optional[FusedNode]] = {}
        self.__backup_code_position = backup_code_position
        self.__fusion_accessor = FusionAccessor(
            number_of_primaries=cluster_information.number_of_primaries,
            number_of_faults=cluster_information.number_of_faults
        )

    @property
    def _data_stack(self) -> DoublyLinkedList[FusedNode]:
        return self.__data_stack

    @property
    def backup_code_position(self) -> int:
        return self.__backup_code_position

    @property
    def fusion_accessor(self) -> FusionAccessor:
        return self.__fusion_accessor

    @property
    @abstractmethod
    def structure_type(self) -> StructureType:
        pass

    def register_primary_structure_identifier(self, primary_structure_identifier: str) -> None:
        if self._registration_lock:
            raise Exception("All expected primaries have already been registered to this structure")

        self.primary_structure_identifiers.append(primary_structure_identifier)
        self.__fused_node_top_of_stack[primary_structure_identifier] = None

        if len(self.primary_structure_identifiers) == self.number_of_primaries:
            self._registration_lock = True

    def _add(self, element, primary_structure_identifier: str) -> FusedAuxNode:
        """Create/add to fused node logic and return it so the caller function can use it to add to aux structure"""
        if not self._registration_lock:
            raise Exception("Not all expected primaries have been registered to this structure")

        node_to_update: FusedNode
        # logic to find which fused node to update
        if self.__data_stack.is_empty() or self.__fused_node_top_of_stack[primary_structure_identifier] == self.__data_stack.get_last():
            node_to_update = FusedNode(primary_structure_identifiers=self.primary_structure_identifiers)
            self.__data_stack.insert_end(node_to_update)
        else:
            if self.__fused_node_top_of_stack[primary_structure_identifier] is None:
                node_to_update = self.__data_stack.get_first()
            else:
                node_to_update = self.__data_stack.get_next(self.__fused_node_top_of_stack[primary_structure_identifier])
        self.__fused_node_top_of_stack[primary_structure_identifier] = node_to_update

        node_to_update.add_element(element, primary_structure_identifier, self.backup_code_position, self.fusion_accessor)

        aux_node = FusedAuxNode(fused_node=node_to_update)
        node_to_update.aux_nodes[primary_structure_identifier] = aux_node

        return aux_node

    def _remove(self, element, final_element, aux_node: FusedAuxNode, primary_structure_identifier: str):
        """Remove data from fused node and return it so the caller function can use it to add to aux structure"""

        node_to_update = aux_node.fused_node

        if node_to_update != self.__fused_node_top_of_stack[primary_structure_identifier]:
            # hole has been created
            node_to_update.remove_element(
                element, primary_structure_identifier, self.backup_code_position, self.fusion_accessor
            )
            node_to_update.add_element(
                final_element, primary_structure_identifier, self.backup_code_position, self.fusion_accessor
            )
            final_aux_node = self.__fused_node_top_of_stack[primary_structure_identifier].aux_nodes[primary_structure_identifier]
            final_aux_node.fused_node = node_to_update
            node_to_update.aux_nodes[primary_structure_identifier] = final_aux_node
            self.__fused_node_top_of_stack[primary_structure_identifier].aux_nodes[primary_structure_identifier] = None

        self.__fused_node_top_of_stack[primary_structure_identifier].remove_element(
            final_element, primary_structure_identifier, self.backup_code_position, self.fusion_accessor
        )
        final_node: FusedNode = self.__fused_node_top_of_stack[primary_structure_identifier]

        if final_node.is_empty():
            self.__data_stack.pop()

        self.__fused_node_top_of_stack[primary_structure_identifier] = self.__data_stack.get_previous(
            self.__fused_node_top_of_stack[primary_structure_identifier]
        )

    def get_fused_data(self) -> List[int]:
        data = []

        node: Optional[FusedNode] = self._data_stack.get_first()
        while node is not None:
            data.append(node.encoded_data)
            node = self._data_stack.get_next(node)

        return data

    @abstractmethod
    def get_index_data(self) -> List[List[int]]:
        pass
