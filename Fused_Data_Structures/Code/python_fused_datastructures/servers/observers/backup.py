import sys
import logging

from protos.service_pb2 import StructureMutation, FusedRemoveValuePayload, \
    FusedAddValuePayload, StructureType
from ..shared.events import MutationEvent, RemoveItemEvent, SetItemEvent


async def backup_observer(event: MutationEvent) -> None:
    if isinstance(event, SetItemEvent):
        if event.old_value:
            payload = FusedAddValuePayload(
                index=event.index,
                value=event.value,
                oldValue=event.old_value
            )
        else:
            payload = FusedAddValuePayload(
                index=event.index,
                value=event.value,
            )

        mutation = StructureMutation(
            structureIdentifier=event.structure_identifier,
            fusedAddValuePayload=payload,
            clusterIdentifier=event.cluster_identifier
        )

        logging.info(
            f"Primary node sending mutation to backup servers for primary structure identifier {event.structure_identifier}:"
        )

        if event.old_value:
            if event.structure_type == StructureType.MAP:
                logging.info(
                    f"Event=set, Key={event.index}, Value={event.value}, OldValue={event.old_value}\n")
        else:
            if event.structure_type == StructureType.LIST:
                logging.info(
                    f"Event=insert, Index={event.index}, Value={event.value}\n")
            elif event.structure_type == StructureType.MAP:
                logging.info(f"Event=set, Key={event.index}, Value={event.value}\n")
            elif event.structure_type == StructureType.QUEUE:
                logging.info(f"Event=enqueue, Value={event.value}\n")

        await event.backup_connection_manager.send_mutation_to_all_connections(mutation)

    elif isinstance(event, RemoveItemEvent):
        payload = FusedRemoveValuePayload(
            index=event.index, value=event.value, valueToReplaceWith=event.value_to_replace_with
        )
        mutation = StructureMutation(
            structureIdentifier=event.structure_identifier,
            fusedRemoveValuePayload=payload,
            clusterIdentifier=event.cluster_identifier
        )

        logging.info(
            f"Primary node sending mutation to backup servers for primary structure identifier {event.structure_identifier}:"
        )
        if event.structure_type == StructureType.LIST:
            logging.info(
                f"Event=remove, Index={event.index}, Value={event.value}, ValueToReplaceWith={event.value_to_replace_with}\n")
        elif event.structure_type == StructureType.MAP:
            logging.info(
                f"Event=remove, Key={event.index}, Value={event.value}, ValueToReplaceWith={event.value_to_replace_with}\n")
        elif event.structure_type == StructureType.QUEUE:
            logging.info(
                f"Event=dequeue, Value={event.value}, ValueToReplaceWith={event.value_to_replace_with}\n")

        await event.backup_connection_manager.send_mutation_to_all_connections(mutation)

    sys.stdout.flush()
