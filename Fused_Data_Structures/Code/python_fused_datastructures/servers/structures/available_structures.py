from typing import Dict, Type

from protos.service_pb2 import StructureType
from servers.structures.fused.fused_list import FusedList
from servers.structures.fused.fused_map import FusedMap
from servers.structures.fused.fused_queue import FusedQueue
from servers.structures.primary.interface import PrimaryStructure
from servers.structures.fused.interface import FusedStructure
from servers.structures.primary.primary_list import PrimaryList
from servers.structures.primary.primary_map import PrimaryMap
from servers.structures.primary.primary_queue import PrimaryQueue

primary_structures: Dict["StructureType", Type[PrimaryStructure]] = {
    StructureType.LIST: PrimaryList,
    StructureType.MAP: PrimaryMap,
    StructureType.QUEUE: PrimaryQueue,
}

fused_structures: Dict["StructureType", Type[FusedStructure]] = {
    StructureType.LIST: FusedList,
    StructureType.MAP: FusedMap,
    StructureType.QUEUE: FusedQueue,
}
