import logging
from typing import List

from protos.service_pb2 import CreateFusedStructureRequest, StructureMutation, StructureType
from servers.backup.connection import BackupStructureConnection


class BackupStructureConnectionManager:
    def __init__(self, backup_ports: List[int]):
        self.__backup_ports = backup_ports
        self.__backup_connections: List[BackupStructureConnection] = []

    async def establish_backup_connections(self):
        logging.info(
            f"Initializing connections to backup nodes on ports: {self.__backup_ports}")
        for backup_port in self.__backup_ports:
            connection = BackupStructureConnection(backup_port)
            await connection.establish_node_connection()
            self.__backup_connections.append(connection)

    async def create_fused_structure_on_all_backups(
        self,
        structure_type: StructureType,
        primary_structure_identifier: str,
        cluster_identifier: str,
        number_of_primaries: int,
        number_of_faults: int
    ) -> None:
        for i, connection in enumerate(self.__backup_connections):
            payload = CreateFusedStructureRequest(
                type=structure_type,
                primaryStructureIdentifier=primary_structure_identifier,
                clusterIdentifier=cluster_identifier,
                numberOfPrimaries=number_of_primaries,
                numberOfFaults=number_of_faults,
                backupCodePosition=i
            )

            await connection.stub.CreateFusedStructure(payload)

    async def send_mutation_to_all_connections(self, mutation: StructureMutation):
        for connection in self.__backup_connections:
            await connection.stub.MutationStream(mutation)

    async def close_backup_connections(self):
        for connection in self.__backup_connections:
            await connection.close_node_connection()
