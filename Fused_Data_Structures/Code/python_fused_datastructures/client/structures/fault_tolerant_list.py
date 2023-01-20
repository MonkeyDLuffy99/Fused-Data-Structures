from typing import List

from client.structures.interface import FaultTolerantInterface

from protos.service_pb2 import StructureType


class FaultTolerantList(FaultTolerantInterface):
    async def create(self):
        await super().establish_node_connection()
        await super().create_structure(structure_type=StructureType.LIST)

    async def get_all_values(self) -> List:
        values = await self._get_all_values()

        value_list = [values[key] for key in sorted(values.keys())]

        return value_list

    async def insert(self, index: int, value: int) -> None:
        """Insert `value` to list at position `index`"""
        await self._add(index, value)

    async def remove(self, index: int) -> None:
        """Remove element at position `index`"""
        await self._remove(index)
