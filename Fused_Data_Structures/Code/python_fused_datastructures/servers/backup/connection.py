from typing import Optional

import grpc
import logging

from protos.service_pb2_grpc import FusedDataStructureStub


class BackupStructureConnection:
    def __init__(
        self, backup_port: int
    ):
        self.__connection: Optional[FusedDataStructureStub] = None
        self.__backup_port: int = backup_port
        self.__channel = grpc.aio.insecure_channel(f"localhost:{self.__backup_port}")

    async def establish_node_connection(self) -> None:
        self.__connection = FusedDataStructureStub(self.__channel)

    async def close_node_connection(self) -> None:
        logging.info(f"Closing node connection on port: {self.__backup_port}")
        await self.__channel.close()

    @property
    def stub(self) -> FusedDataStructureStub:
        return self.__connection
