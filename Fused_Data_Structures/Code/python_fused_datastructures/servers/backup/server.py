import asyncio
import logging

import grpc
from servers.backup.registry import FusedStructureRegistry
from servers.shared.events import RemoveItemEvent, SetItemEvent
from protos.service_pb2 import (
    CreateFusedStructureRequest,
    CreateFusedStructureResponse,
    StructureMutation, FusedRecoveryDataRequest, FusedRecoveryDataResponse, FusedIndexPayload,
)
from protos.service_pb2_grpc import (
    FusedDataStructureServicer,
    add_FusedDataStructureServicer_to_server,
)
from shared.types import ClusterInformation


class BackupNodeServicer(FusedDataStructureServicer):
    def __init__(self) -> None:
        self.__registry = FusedStructureRegistry()

    def CreateFusedStructure(
        self, request: CreateFusedStructureRequest, _
    ) -> CreateFusedStructureResponse:
        # Register a new structure based on the requested type
        structure = self.__registry.create(
            request.type,
            request.primaryStructureIdentifier,
            ClusterInformation(
                request.clusterIdentifier,
                request.numberOfPrimaries,
                request.numberOfFaults
            ),
            request.backupCodePosition
        )

        # Return the identifier of the new structure in the response
        return CreateFusedStructureResponse(structureIdentifier=structure.identifier)

    async def MutationStream(self, mutation: StructureMutation, _) -> StructureMutation:
        # Retrieve the structure from the registry
        structure = self.__registry.get(mutation.clusterIdentifier)

        if structure is None:
            return None

        # Convert the payload into a local event
        if mutation.WhichOneof("event") == "fusedAddValuePayload":
            event = SetItemEvent(
                {
                    "index": mutation.fusedAddValuePayload.index,
                    "value": mutation.fusedAddValuePayload.value,
                    "oldValue": mutation.fusedAddValuePayload.oldValue
                },
                mutation.clusterIdentifier,
                mutation.structureIdentifier,
                structure.structure_type
            )
        elif mutation.WhichOneof("event") == "fusedRemoveValuePayload":
            event = RemoveItemEvent(
                {
                    "index": mutation.fusedRemoveValuePayload.index,
                    "value": mutation.fusedRemoveValuePayload.value,
                    "valueToReplaceWith": mutation.fusedRemoveValuePayload.valueToReplaceWith
                },
                mutation.clusterIdentifier,
                mutation.structureIdentifier,
                structure.structure_type
            )
        else:
            return None

        # Pass the event to the data structure
        await structure.process_event(event)

        # Echo the mutation back to the requester
        return mutation

    def GetFusedRecoveryData(self, request: FusedRecoveryDataRequest, _) -> FusedRecoveryDataResponse:
        structure = self.__registry.get(request.clusterIdentifier)

        index_data = structure.get_index_data()

        payload_index = []
        for data in index_data:
            payload_index.append(FusedIndexPayload(fusedDataIndexes=data))

        return FusedRecoveryDataResponse(
            fusedData=structure.get_fused_data(),
            indexData=payload_index
        )


async def backup_server_thread(port: int) -> None:
    server = grpc.aio.server()
    add_FusedDataStructureServicer_to_server(BackupNodeServicer(), server)
    server.add_insecure_port(f"[::]:{port}")

    await server.start()
    await server.wait_for_termination()


def start_backup_server(port: int) -> None:
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(backup_server_thread(port))
