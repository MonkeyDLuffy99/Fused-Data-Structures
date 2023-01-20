from typing import List, Dict

from protos.service_pb2 import ValueRequest, AddValuePayload, StructureMutation, RemoveValuePayload, \
    CreatePrimaryStructureRequest, StructureType
from protos.service_pb2_grpc import PrimaryDataStructureStub
from shared.types import ClusterInformation


async def create_primary_structure(
    stub: PrimaryDataStructureStub,
    structure_type: StructureType,
    backup_ports: List[int],
    cluster_information: ClusterInformation
) -> str:
    request = CreatePrimaryStructureRequest(
        type=structure_type,
        backupPorts=backup_ports,
        clusterIdentifier=cluster_information.cluster_identifier,
        numberOfPrimaries=cluster_information.number_of_primaries,
        numberOfFaults=cluster_information.number_of_faults
    )
    value = await stub.CreatePrimaryStructure(request)

    return value.structureIdentifier


async def get_value(
    stub: PrimaryDataStructureStub, structure_identifier: str, key: str
) -> int:
    request = ValueRequest(
        structureIdentifier=structure_identifier, key=key
    )
    value = await stub.GetValue(request)

    return value.value


async def get_all_values(
    stub: PrimaryDataStructureStub,
    structure_identifier: str,
) -> Dict[int, int]:
    request = ValueRequest(
        structureIdentifier=structure_identifier
    )
    values = await stub.GetAllValues(request)

    return values.values


async def add_value(
    stub: PrimaryDataStructureStub,
    structure_identifier: str,
    index: int,
    value: int,
    cluster_identifier: str
) -> None:
    payload = AddValuePayload(index=index, value=value)

    mutation = StructureMutation(
        structureIdentifier=structure_identifier,
        addValuePayload=payload,
        clusterIdentifier=cluster_identifier
    )

    await stub.MutationStream(mutation)


async def remove_value(
    stub: PrimaryDataStructureStub,
    structure_identifier: str,
    index: int,
    cluster_identifier: str
) -> None:
    payload = RemoveValuePayload(index=index)

    mutation = StructureMutation(
        structureIdentifier=structure_identifier,
        removeValuePayload=payload,
        clusterIdentifier=cluster_identifier
    )

    await stub.MutationStream(mutation)
