import asyncio
import logging

import grpc

from shared.types import ClusterInformation
from .registry import PrimaryStructureRegistry
from servers.shared.events import RemoveItemEvent, SetItemEvent
from protos.service_pb2 import (
    CreatePrimaryStructureRequest,
    CreatePrimaryStructureResponse,
    StructureMutation,
    ValueRequest,
    ValueResponse, AllValuesRequest, AllValuesResponse,
)
from protos.service_pb2_grpc import (
    PrimaryDataStructureServicer,
    add_PrimaryDataStructureServicer_to_server,
)
from servers.structures.primary.primary_list import PrimaryList
from ..structures.primary.interface import PrimaryNode


class PrimaryNodeServicer(PrimaryDataStructureServicer):
    def __init__(self) -> None:
        self.__registry = PrimaryStructureRegistry()

    async def CreatePrimaryStructure(
        self, request: CreatePrimaryStructureRequest, _
    ) -> CreatePrimaryStructureResponse:
        # Register a new structure based on the requested type
        structure = await self.__registry.create(
            request.type,
            ClusterInformation(request.clusterIdentifier,
                               request.numberOfPrimaries, request.numberOfFaults),
            request.backupPorts,
        )
        # Return the identifier of the new structure in the response
        return CreatePrimaryStructureResponse(structureIdentifier=structure.identifier)

    def GetValue(self, request: ValueRequest, _) -> ValueResponse:
        # Retrieve the structure from the registry
        structure = self.__registry.get(request.structureIdentifier)

        if structure is None:
            return None

        # Convert the index based on the structure type
        # key = int(request.key) if isinstance(structure, PrimaryList) else request.key
        key = int(request.key)
        primary_node: PrimaryNode = structure[key]

        # Return the value at the specified key in the structure
        return ValueResponse(value=primary_node.value)

    def GetAllValues(self, request: AllValuesRequest, _) -> AllValuesResponse:
        # Retrieve the structure from the registry
        structure = self.__registry.get(request.structureIdentifier)

        if structure is None:
            return None

        # Return the value at the specified key in the structure
        return AllValuesResponse(values=structure.values_as_map)

    async def MutationStream(self, mutation: StructureMutation, _) -> StructureMutation:
        # Retrieve the structure from the registry
        structure = self.__registry.get(mutation.structureIdentifier)

        if structure is None:
            return None

        # Convert the payload into a local event
        if mutation.WhichOneof("event") == "addValuePayload":
            event = SetItemEvent(
                {
                    "index": mutation.addValuePayload.index,
                    "value": mutation.addValuePayload.value,
                },
                mutation.clusterIdentifier,
                structure.identifier,
                structure.structure_type
            )
        else:
            # elif mutation.WhichOneof("event") == "removeValuePayload":\
            event = RemoveItemEvent(
                {"index": mutation.removeValuePayload.index},
                mutation.clusterIdentifier,
                structure.identifier,
                structure.structure_type
            )

        # Pass the event to the data structure
        await structure.process_event(event)

        # Echo the mutation back to the requester
        return mutation


async def primary_server_thread(port: int) -> None:
    server = grpc.aio.server()
    add_PrimaryDataStructureServicer_to_server(PrimaryNodeServicer(), server)
    server.add_insecure_port(f"[::]:{port}")

    await server.start()
    await server.wait_for_termination()


def start_primary_server(port: int) -> None:
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(primary_server_thread(port))
