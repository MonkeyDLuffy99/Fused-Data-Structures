import asyncio
import logging
import time

from python_fused_datastructures.client.clusters.fault_tolerant_list_cluster import FaultTolerantListCluster
from python_fused_datastructures.client.nodes.manager import (
    start_nodes,
    stop_nodes,
)

NUM_PRIMARIES = 3
NUM_FAULTS = 3


async def test_list() -> None:
    # Start primary and backup nodes
    node_processes = start_nodes(NUM_PRIMARIES, NUM_FAULTS)
    time.sleep(1)

    # Create client objects to interface with the nodes that we have just started.
    # A cluster represents a group of fused structures, since each primary node can store multiple structures.
    cluster_client_1 = FaultTolerantListCluster(node_processes)
    cluster_client_2 = FaultTolerantListCluster(node_processes)

    # Register the existince of each cluster with the nodes
    await cluster_client_1.register_structures()
    await cluster_client_2.register_structures()

    # Add some items to each of the lists in cluster 1
    for record in [
        {'primary': 0, 'insert_index': 0, 'value': 123},
        {'primary': 0, 'insert_index': 1, 'value': 456},
        {'primary': 1, 'insert_index': 0, 'value': 456},
        {'primary': 2, 'insert_index': 0, 'value': 789},
        {'primary': 1, 'insert_index': 0, 'value': 555},
        {'primary': 0, 'insert_index': 2, 'value': 789},
    ]:
        await cluster_client_1[record['primary']].insert(record['insert_index'], record['value'])

    # Add some items the lists in cluster 2
    await cluster_client_2[0].insert(0, 111)
    await cluster_client_2[1].insert(0, 222)
    await cluster_client_2[1].insert(0, 333)

    # Fetch some values from the first list in cluster 1
    for key in [0, 1, 2]:
        logging.info(f"Retrieved value for list cluster `1`, primary list `0` at index `0`: {await cluster_client_1[0].get(key)}\n")

    # Simulate the fault of all three primaries in cluster 1
    await cluster_client_1.recreate_structures({0, 1, 2})

    # Delete some items from each cluster
    await cluster_client_1.data[2].remove(0)
    await cluster_client_2.data[1].remove(1)

    # Stop the primary and backup nodes
    stop_nodes(node_processes.processes)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(test_list())
