import multiprocessing
from typing import NamedTuple, List


class ClusterInformation(NamedTuple):
    cluster_identifier: str
    number_of_primaries: int
    number_of_faults: int


class NodeProcesses(NamedTuple):
    primary_ports: List[int]
    backup_ports: List[int]
    processes: List[multiprocessing.Process]
    number_of_primaries: int
    number_of_faults: int
