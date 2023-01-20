import asyncio
import logging
import time

from python_fused_datastructures.client.clusters.fault_tolerant_map_cluster import FaultTolerantMapCluster
from python_fused_datastructures.client.nodes.manager import (
    start_nodes,
    stop_nodes,
)

NUM_PRIMARIES = 3
NUM_FAULTS = 3


async def test_map() -> None:
    # Start primary and backup nodes
    node_processes = start_nodes(NUM_PRIMARIES, NUM_FAULTS)
    time.sleep(1)

    # Create client objects to interface with the nodes that we have just started.
    # A cluster represents a group of fused structures, since each primary node can store multiple structures.
    cluster_client_1 = FaultTolerantMapCluster(node_processes)
    cluster_client_2 = FaultTolerantMapCluster(node_processes)

    # Register the existince of each cluster with the nodes
    await cluster_client_1.register_structures()
    await cluster_client_2.register_structures()

    # Add some items to each of the maps in cluster 1
    for record in [
        {'primary': 0, 'key': 0, 'value': 123},
        {'primary': 0, 'key': 1, 'value': 456},
        {'primary': 1, 'key': 0, 'value': 456},
        {'primary': 2, 'key': 0, 'value': 789},
        {'primary': 1, 'key': 0, 'value': 555},
        {'primary': 0, 'key': 2, 'value': 789},
    ]:
        await cluster_client_1[record['primary']].put(record['key'], record['value'])

    # Add some items the maps in cluster 2
    await cluster_client_2[0].put(0, 111)
    await cluster_client_2[1].put(0, 222)
    await cluster_client_2[1].put(1, 333)

    # Fetch some values from the first map in cluster 1
    for key in [0, 1, 2]:
        logging.info(f"Retrieved value for map cluster `1`, primary map `0` at index `{key}`: {await cluster_client_1[0].get(key)}\n")

    # Simulate the fault of all three primaries in cluster 1
    await cluster_client_1.recreate_structures({0, 1, 2})

    # Delete some items from each cluster
    await cluster_client_1.data[2].remove(0)
    await cluster_client_2.data[1].remove(1)

    # Stop the primary and backup nodes
    stop_nodes(node_processes.processes)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(test_map())
