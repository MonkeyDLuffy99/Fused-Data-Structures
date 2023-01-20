import asyncio
import logging
import time

from python_fused_datastructures.client.clusters.fault_tolerant_queue_cluster import FaultTolerantQueueCluster
from python_fused_datastructures.client.nodes.manager import (
    start_nodes,
    stop_nodes,
)

NUM_PRIMARIES = 3
NUM_FAULTS = 3


async def test_queue() -> None:
    # Start primary and backup nodes
    node_processes = start_nodes(NUM_PRIMARIES, NUM_FAULTS)
    time.sleep(1)

    # Create a client object to interface with the nodes that we have just started.
    # A cluster represents a group of fused structures, since each primary node can store multiple structures.
    queue_cluster_client = FaultTolerantQueueCluster(node_processes)
    await queue_cluster_client.register_structures()

    # Add some items to the queue
    await queue_cluster_client[0].enqueue(5)
    await queue_cluster_client[0].enqueue(6)
    await queue_cluster_client[0].enqueue(7)
    logging.info(f"Front of queue: {await queue_cluster_client[0].peek()}")

    # Remove an item from the queue
    await queue_cluster_client[0].dequeue()
    logging.info(f"Front of queue: {await queue_cluster_client[0].peek()}")

    # Simulate the failure of all primary nodes
    await queue_cluster_client.recreate_structures({0, 1, 2})

    # Stop the primary and backup nodes
    stop_nodes(node_processes.processes)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(test_queue())
