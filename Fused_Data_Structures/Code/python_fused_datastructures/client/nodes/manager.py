import logging
import multiprocessing

from typing import List

from servers.primary.server import start_primary_server
from servers.backup.server import start_backup_server
from shared.types import NodeProcesses


def start_nodes(
    number_of_primaries: int, number_of_faults: int, port_start: int = 50000
) -> NodeProcesses:
    logging.info("Starting nodes...")
    processes = []

    primary_ports = [port_start + i for i in range(number_of_primaries)]
    for port in primary_ports:
        processes.append(
            multiprocessing.Process(target=start_primary_server, args=(port,))
        )

    backup_ports = [port_start + number_of_primaries +
                    i for i in range(number_of_faults)]
    for port in backup_ports:
        processes.append(
            multiprocessing.Process(target=start_backup_server, args=(port,))
        )

    for process in processes:
        process.start()

    logging.info(f"Primary ports: {primary_ports}")
    logging.info(f"Backup ports: {backup_ports}\n")

    return NodeProcesses(primary_ports, backup_ports, processes, number_of_primaries, number_of_faults)


def stop_nodes(processes: List[multiprocessing.Process]) -> None:
    logging.info("Stopping nodes...")

    for process in processes:
        process.terminate()
        process.join()
