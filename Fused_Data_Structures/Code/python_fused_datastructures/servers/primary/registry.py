# StructureRegistry tracks data structures that this node is storing
from typing import Dict, Optional, List

from servers.structures.primary.interface import PrimaryStructure
from servers.structures.available_structures import primary_structures
from protos.service_pb2 import StructureType
from shared.types import ClusterInformation


class PrimaryStructureRegistry:
    def __init__(self) -> None:
        self.__structures: Dict[str, PrimaryStructure] = {}
        self.__available_structures = primary_structures

    async def create(
        self,
        structure_type: StructureType,
        cluster_information: ClusterInformation,
        backup_ports: List[int],
    ) -> PrimaryStructure:
        structure_generator = self.__available_structures.get(structure_type)
        if structure_generator is None:
            raise Exception("Unrecognised structure type")

        structure = structure_generator(cluster_information, backup_ports)
        await structure.create_backup_connections()

        self.__structures[structure.identifier] = structure
        return structure

    def get(self, structure_identifier: str) -> Optional[PrimaryStructure]:
        return self.__structures.get(structure_identifier)
