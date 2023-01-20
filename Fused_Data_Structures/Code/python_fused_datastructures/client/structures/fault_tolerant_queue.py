from typing import List

from client.structures.interface import FaultTolerantInterface

from protos.service_pb2 import StructureType


class FaultTolerantQueue(FaultTolerantInterface):
    async def create(self):
        await super().establish_node_connection()
        await super().create_structure(structure_type=StructureType.QUEUE)

    async def get_all_values(self) -> List:
        values = await self._get_all_values()

        value_list = [values[key] for key in sorted(values.keys())]

        return value_list

    async def enqueue(self, value: int) -> None:
        """Add an item to end of queue"""
        # Only value is used within primary and fused structure - key/index can be random value
        await self._add(0, value)

    async def dequeue(self) -> int:
        """Return and remove the element at front of queue"""
        value = await self.get(0)
        await self._remove(0)

        return value

    async def peek(self) -> int:
        """Returns element at front of queue - synonymous to get(0)"""
        return await self.get(0)
