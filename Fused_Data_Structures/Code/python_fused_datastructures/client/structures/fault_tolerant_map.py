from typing import Dict

from client.structures.interface import FaultTolerantInterface

from protos.service_pb2 import StructureType


class FaultTolerantMap(FaultTolerantInterface):
    async def create(self):
        await super().establish_node_connection()
        await super().create_structure(structure_type=StructureType.MAP)

    async def get_all_values(self) -> Dict:
        values = await self._get_all_values()

        return values

    async def put(self, key: int, value: int) -> None:
        """Put `value` at specified `key` into map"""
        await self._add(key, value)

    async def remove(self, key: int) -> None:
        """Remove specified `key` from map"""
        await self._remove(key)
