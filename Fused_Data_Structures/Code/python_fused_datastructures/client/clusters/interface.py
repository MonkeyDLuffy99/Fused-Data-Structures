from abc import ABC, abstractmethod
from typing import List, Dict
from uuid import uuid4

import grpc
import logging

from protos.service_pb2 import StructureType, FusedRecoveryDataRequest
from protos.service_pb2_grpc import FusedDataStructureStub
from shared.fusion import FusionAccessor
from shared.types import ClusterInformation, NodeProcesses


class FaultTolerantClusterInterface(ABC):
    """
    Interface for producing a cluster amongst primary and backup ports
    """

    def __init__(self, node_processes: NodeProcesses, structure_type: StructureType):
        self.__structure_type = structure_type
        self.__primary_ports = node_processes.primary_ports
        self.__backup_ports = node_processes.backup_ports
        self.__cluster_info = ClusterInformation(
            cluster_identifier=str(uuid4()),
            number_of_primaries=node_processes.number_of_primaries,
            number_of_faults=node_processes.number_of_faults
        )
        self.primary_structure_identifiers: List[str] = []

    @abstractmethod
    async def register_structures(self):
        pass

    @property
    def structure_type(self) -> StructureType:
        return self.__structure_type

    @property
    def primary_ports(self) -> List[int]:
        return self.__primary_ports

    @property
    def backup_ports(self) -> List[int]:
        return self.__backup_ports

    @property
    def cluster_information(self) -> ClusterInformation:
        return self.__cluster_info

    @property
    def cluster_identifier(self) -> str:
        return self.cluster_information.cluster_identifier

    async def _recover_data(self, available_data, detected_faults) -> Dict[str, Dict[int, int]]:
        available_fused_data: List[List[int]] = []
        available_index_data = []
        available_rs_data = []
        index_data_received = False

        # Connect to fused structures and get all data
        for backup_port in self.backup_ports:
            channel = grpc.aio.insecure_channel(
                f"localhost:{backup_port}"
            )
            stub = FusedDataStructureStub(channel)
            response = await stub.GetFusedRecoveryData(
                FusedRecoveryDataRequest(clusterIdentifier=self.cluster_identifier)
            )

            fused_data = response.fusedData
            available_fused_data.append(fused_data)

            if not index_data_received:
                index_data = response.indexData
                for x in index_data:
                    available_index_data.append(x.fusedDataIndexes)
                index_data_received = True

            await channel.close()

        logging.info(f"Available auxiliary data: {available_index_data}")

        fusion_accessor = FusionAccessor(number_of_primaries=self.cluster_information.number_of_primaries,
                                         number_of_faults=self.cluster_information.number_of_faults)
        restored_data_arrays = []
        for i in range(len(available_index_data)):
            code = []
            data = []

            for j in range(self.cluster_information.number_of_faults):
                code.append(available_fused_data[j][i])

            for j, primary_structure_identifier in enumerate(self.primary_structure_identifiers):
                index_of_primary = available_index_data[i][j]

                if j not in detected_faults and index_of_primary != -1:
                    original = available_data[primary_structure_identifier]
                    data.append(original[index_of_primary])
                else:
                    data.append(0)

            # Build list of erasures from detected faults
            erasures = list(detected_faults)
            while len(erasures) < self.cluster_information.number_of_faults + 1:
                erasures.append(-1)

            restored_data = fusion_accessor.get_recovered_data(code, data, erasures)
            restored_data_arrays.append(restored_data)
            available_rs_data.append(code)

        recovered_data_mapping = {x: {} for x in self.primary_structure_identifiers}
        for i, indexes in enumerate(available_index_data):
            for j, key in enumerate(indexes):
                if key == -1:
                    continue
                recovered_data_mapping[self.primary_structure_identifiers[j]
                                       ][key] = restored_data_arrays[i][j]

        logging.info(f"Available RS-encoded data: {[*zip(*available_rs_data)]}")

        return recovered_data_mapping
