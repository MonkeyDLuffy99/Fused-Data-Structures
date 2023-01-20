from typing import List, Set, Dict

import logging

from client.clusters.interface import FaultTolerantClusterInterface
from client.structures.fault_tolerant_queue import FaultTolerantQueue
from shared.types import NodeProcesses
from protos.service_pb2 import StructureType


class FaultTolerantQueueCluster(FaultTolerantClusterInterface):
    def __init__(self, node_processes: NodeProcesses):
        super().__init__(node_processes, StructureType.LIST)
        self.data: List[FaultTolerantQueue] = []

    def __getitem__(self, item) -> FaultTolerantQueue:
        return self.data[item]

    async def register_structures(self) -> None:
        logging.info(
            f"Creating fault tolerant queue cluster with identifier: {self.cluster_identifier}")
        for primary_port in self.primary_ports:
            logging.info(
                f"Initializing primary queue on primary node on port: {primary_port}")
            f_queue = FaultTolerantQueue(
                primary_port, self.backup_ports, self.cluster_information)
            await f_queue.create()
            self.data.append(f_queue)
            self.primary_structure_identifiers.append(f_queue.identifier)

    async def recreate_structures(self, detected_faults: Set[int]):
        if len(detected_faults) > self.cluster_information.number_of_faults:
            raise Exception(
                "Unable to recreate primary structures as too many faults detected")

        logging.info(
            f"Attempting to recreate original data for {len(detected_faults)} faults on data points: {detected_faults}")
        available_data: Dict[str, List] = {x: []
                                           for x in self.primary_structure_identifiers}

        for i, structure in enumerate(self.data):
            if i in detected_faults:
                continue

            # Primary data that we do have
            values = await structure.get_all_values()
            available_data[structure.identifier] = values

        logging.info(f"Available primary data: {available_data}")

        recovered_data_as_map = await self._recover_data(available_data, detected_faults)
        recovered_lists = {}
        for i, data_map in recovered_data_as_map.items():
            sorted_keys = sorted(data_map.keys())
            recovered_list = []
            for j, key in enumerate(sorted_keys):
                if j != key:
                    raise Exception("Keys must represent position in list")
                recovered_list.append(data_map[key])

            recovered_lists[i] = recovered_list

        logging.info(f"\nQueues that were restored:")
        for faulty_data_ordinal in detected_faults:
            primary_structure_identifier = self.primary_structure_identifiers[faulty_data_ordinal]
            logging.info(f"Primary structure `{faulty_data_ordinal}` with structure identifier "
                         f"`{primary_structure_identifier}` was recovered: {recovered_lists[primary_structure_identifier]}")
        logging.info("Data restoration complete...\n")
