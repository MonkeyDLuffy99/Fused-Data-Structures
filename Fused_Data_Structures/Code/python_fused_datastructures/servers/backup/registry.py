# StructureRegistry tracks data structures that this node is storing
from typing import Dict, Optional

from servers.structures.fused.interface import FusedStructure
from servers.structures.available_structures import fused_structures
from protos.service_pb2 import StructureType
from shared.types import ClusterInformation


class FusedStructureRegistry:
    def __init__(self) -> None:
        self.__structures: Dict[str, FusedStructure] = {}
        self.__available_structures = fused_structures
        self.__system_structure_mapping: Dict[str, str] = {}

    def create(
        self,
        structure_type: StructureType,
        primary_structure_identifier: str,
        cluster_information: ClusterInformation,
        backup_code_position: int
    ) -> FusedStructure:
        # Only create a new fused structure if one does not exist for the system
        structure_identifier = self.__system_structure_mapping.get(cluster_information.cluster_identifier)

        if structure_identifier is None:
            structure_generator = self.__available_structures.get(structure_type)
            if structure_generator is None:
                raise Exception("Unrecognised structure type")

            structure = structure_generator(cluster_information, backup_code_position)
            self.__structures[structure.identifier] = structure
            self.__system_structure_mapping[cluster_information.cluster_identifier] = structure.identifier
        else:
            structure = self.__structures[structure_identifier]

        structure.register_primary_structure_identifier(primary_structure_identifier)

        return structure

    def get(self, cluster_identifier: str) -> Optional[FusedStructure]:
        structure_identifier = self.__system_structure_mapping.get(cluster_identifier)

        if structure_identifier:
            return self.__structures.get(structure_identifier)

        return None
