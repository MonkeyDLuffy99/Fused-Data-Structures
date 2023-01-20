from typing import List, Set, Dict, Optional

import logging

from client.clusters.interface import FaultTolerantClusterInterface
from shared.types import NodeProcesses
from client.structures.fault_tolerant_map import FaultTolerantMap
from protos.service_pb2 import StructureType


class FaultTolerantMapCluster(FaultTolerantClusterInterface):
    def __init__(self, node_processes: NodeProcesses):
        super().__init__(node_processes, StructureType.MAP)
        self.data: List[FaultTolerantMap] = []

    def __getitem__(self, item) -> FaultTolerantMap:
        return self.data[item]

    async def register_structures(self) -> None:
        logging.info(
            f"Creating fault tolerant map cluster with identifier: {self.cluster_identifier}")
        for primary_port in self.primary_ports:
            logging.info(
                f"Initializing primary map on primary node on port: {primary_port}")
            f_map = FaultTolerantMap(
                primary_port, self.backup_ports, self.cluster_information)
            await f_map.create()
            self.data.append(f_map)
            self.primary_structure_identifiers.append(f_map.identifier)

    async def recreate_structures(self, detected_faults: Set[int]):
        if len(detected_faults) > self.cluster_information.number_of_faults:
            raise Exception(
                "Unable to recreate primary structures as too many faults detected")

        logging.info(
            f"Attempting to recreate original data for {len(detected_faults)} faults on data points: {detected_faults}")
        available_data: Dict[str, Optional[Dict]] = {
            x: None for x in self.primary_structure_identifiers}

        for i, structure in enumerate(self.data):
            if i in detected_faults:
                continue

            # Primary data that we do have
            values = await structure.get_all_values()
            available_data[structure.identifier] = values

        logging.info(f"Available primary data: {available_data}")

        recovered_maps = await self._recover_data(available_data, detected_faults)

        logging.info(f"\nMaps which were restored:")
        for faulty_data_ordinal in detected_faults:
            primary_structure_identifier = self.primary_structure_identifiers[faulty_data_ordinal]
            logging.info(
                f"Primary structure `{faulty_data_ordinal}` with structure identifier `{primary_structure_identifier}` was recovered: {recovered_maps[primary_structure_identifier]}")
