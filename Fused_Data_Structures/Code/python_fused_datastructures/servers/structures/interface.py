from abc import ABC, abstractmethod
from uuid import uuid4

from servers.shared.events import MutationEvent
from shared.types import ClusterInformation


class Structure(ABC):
    def __init__(self, cluster_information: ClusterInformation):
        self.__identifier = str(uuid4())
        self.__cluster_information = cluster_information

    @abstractmethod
    async def process_event(self, event: MutationEvent) -> None:
        pass

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def cluster_identifier(self) -> str:
        return self.__cluster_information.cluster_identifier

    @property
    def number_of_primaries(self) -> int:
        return self.__cluster_information.number_of_primaries

    @property
    def number_of_faults(self) -> int:
        return self.__cluster_information.number_of_faults
