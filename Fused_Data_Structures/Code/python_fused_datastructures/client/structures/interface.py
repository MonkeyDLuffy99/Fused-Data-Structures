from abc import ABC, abstractmethod
from typing import List, Optional, Coroutine, Dict

import grpc
import logging

from client.structures.helpers import get_value, add_value, remove_value, create_primary_structure, get_all_values
from protos.service_pb2 import StructureType
from protos.service_pb2_grpc import PrimaryDataStructureStub
from shared.types import ClusterInformation


class FaultTolerantInterface(ABC):
    def __init__(
        self,
        primary_node_port: int,
        backup_ports: List[int],
        cluster_information: ClusterInformation
    ):
        self.__identifier: Optional[str] = None
        self.__connection: Optional[PrimaryDataStructureStub] = None
        self.__primary_node_port: int = primary_node_port
        self.__channel = grpc.aio.insecure_channel(
            f"localhost:{self.__primary_node_port}"
        )
        self.__backup_ports = backup_ports
        self.__cluster_information = cluster_information

    async def establish_node_connection(self) -> None:
        self.__connection = PrimaryDataStructureStub(self.__channel)

    @property
    def cluster_information(self) -> ClusterInformation:
        return self.__cluster_information

    @property
    def cluster_identifier(self) -> str:
        return self.cluster_information.cluster_identifier

    @property
    def connection(self) -> Optional[PrimaryDataStructureStub]:
        return self.__connection

    @property
    def backup_ports(self) -> List[int]:
        return self.__backup_ports

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def primary_node_port(self) -> int:
        return self.__primary_node_port

    @abstractmethod
    async def create(self):
        pass

    async def create_structure(self, structure_type: StructureType) -> None:
        if self.connection is None:
            raise Exception("Connection with primary not initialised")

        self.__identifier = await create_primary_structure(self.connection, structure_type, self.backup_ports, self.cluster_information)

    async def close_node_connection(self) -> None:
        logging.info(f"Closing node connection on port: {self.__primary_node_port}")
        await self.__channel.close()

    async def _add(self, index: int, value: int) -> None:
        if self.identifier is None or self.connection is None:
            raise Exception("Connection with primary not initialised")

        await add_value(self.connection, self.identifier, index, value, self.cluster_identifier)

    async def _remove(self, index: int) -> None:
        if self.identifier is None or self.connection is None:
            raise Exception("Connection with primary not initialised")

        await remove_value(self.connection, self.identifier, index, self.cluster_identifier)

    async def get(self, index: int) -> int:
        value = await get_value(self.connection, self.identifier, str(index))
        return value

    @abstractmethod
    async def get_all_values(self):
        pass

    async def _get_all_values(self) -> Dict[int, int]:
        data = await get_all_values(self.connection, self.identifier)
        return data
