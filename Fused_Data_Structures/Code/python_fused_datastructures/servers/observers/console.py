import sys
import logging

from protos.service_pb2 import StructureType
from ..shared.events import MutationEvent, RemoveItemEvent, SetItemEvent


def console_observer(event: MutationEvent) -> None:
    if event.backup_connection_manager and not event.primary_structure_id:
        if isinstance(event, SetItemEvent):
            logging.info(
                f"Primary node received mutation for structure {event.structure_identifier} "
                f"in cluster {event.cluster_identifier}:"
            )
            if event.structure_type == StructureType.LIST:
                logging.info(
                    f"Event=insert, Index={event.index}, Value={event.value}\n")
            elif event.structure_type == StructureType.MAP:
                logging.info(f"Event=set, Key={event.index}, Value={event.value}\n")
            elif event.structure_type == StructureType.QUEUE:
                logging.info(f"Event=enqueue, Value={event.value}\n")

        elif isinstance(event, RemoveItemEvent):
            logging.info(
                f"Primary node received mutation for structure {event.structure_identifier} "
                f"in cluster {event.cluster_identifier}:"
            )
            if event.structure_type == StructureType.LIST:
                logging.info(f"Event=remove, Index={event.index}\n")
            elif event.structure_type == StructureType.MAP:
                logging.info(f"Event=remove, Key={event.index}\n")
            elif event.structure_type == StructureType.QUEUE:
                logging.info(f"Event=dequeue\n")

    elif event.primary_structure_id and not event.backup_connection_manager:
        if isinstance(event, SetItemEvent):
            logging.info(
                f"Backup node received mutation for structure {event.structure_identifier} "
                f"from primary structure {event.primary_structure_id} "
                f"within cluster {event.cluster_identifier}:"
            )
            if event.structure_type == StructureType.LIST:
                logging.info(
                    f"Event=insert, Index={event.index}, Value={event.value}\n")
            elif event.structure_type == StructureType.MAP:
                logging.info(f"Event=set, Key={event.index}, Value={event.value}\n")
            elif event.structure_type == StructureType.QUEUE:
                logging.info(f"Event=enqueue, Value={event.value}\n")

        elif isinstance(event, RemoveItemEvent):
            logging.info(
                f"Backup node received mutation for structure {event.structure_identifier} "
                f"from primary structure {event.primary_structure_id} "
                f"within cluster {event.cluster_identifier}:"
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

    sys.stdout.flush()
