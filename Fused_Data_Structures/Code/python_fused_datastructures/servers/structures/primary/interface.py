from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict
from uuid import uuid4

from protos.service_pb2 import StructureType
from servers.backup.connection_manager import BackupStructureConnectionManager
from servers.structures.generic.doubly_linked_list import DoublyLinkedNode, DoublyLinkedList
from servers.structures.interface import Structure
from shared.types import ClusterInformation


class PrimaryNode(DoublyLinkedNode):
    def __init__(self, value):
        super().__init__()
        self.__identifier = str(uuid4())
        self.value = value
        self.aux_node: Optional[PrimaryAuxNode] = None

    def __repr__(self):
        return self.__identifier + " " + str(self.value)


@dataclass
class PrimaryAuxNode:
    primary_node: PrimaryNode


class PrimaryStructure(Structure):
    def __init__(self, cluster_information: ClusterInformation, backup_ports: List[int]):
        super().__init__(cluster_information)
        self.__backup_connection_manager = BackupStructureConnectionManager(backup_ports)
        self.__data_stack = DoublyLinkedList[PrimaryAuxNode]()

    @property
    def backup_connection_manager(self) -> BackupStructureConnectionManager:
        return self.__backup_connection_manager

    @abstractmethod
    async def create_backup_connections(self) -> None:
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    @property
    @abstractmethod
    def values_as_map(self) -> Dict[int, int]:
        pass

    @property
    @abstractmethod
    def structure_type(self) -> StructureType:
        pass

    async def _create_backup_connections(self, structure_type: StructureType) -> None:
        await self.__backup_connection_manager.establish_backup_connections()
        await self.__backup_connection_manager.create_fused_structure_on_all_backups(
            structure_type=structure_type,
            primary_structure_identifier=self.identifier,
            cluster_identifier=self.cluster_identifier,
            number_of_primaries=self.number_of_primaries,
            number_of_faults=self.number_of_faults
        )

    def _add(self, value) -> PrimaryNode:
        """Creates primary node and adds auxiliary node pointer to data stack"""
        node = PrimaryNode(value)
        aux_node = PrimaryAuxNode(primary_node=node)
        node.aux_node = aux_node
        self.__data_stack.insert_end(aux_node)
        return node

    def _remove(self, primary_node: PrimaryNode) -> PrimaryNode:
        """Removes primary node from auxiliary data stack and returns node that filled gap"""
        final_aux_node: PrimaryAuxNode = self.__data_stack.get_last()
        self.__data_stack.replace_node_with_tail(primary_node.aux_node)
        return final_aux_node.primary_node


