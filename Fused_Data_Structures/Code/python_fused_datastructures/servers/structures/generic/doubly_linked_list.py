from __future__ import annotations

from typing import Optional, TypeVar, Generic

T = TypeVar('T')


class DoublyLinkedNode(Generic[T]):
    def __init__(
        self,
        data: Optional[T] = None,
        previous_node: Optional[DoublyLinkedNode[T]] = None,
        next_node: Optional[DoublyLinkedNode[T]] = None
    ):
        self.__data: Optional[T] = data
        self.previous_node = previous_node
        self.next_node = next_node

    def __repr__(self) -> T:
        return self.__data


class DoublyLinkedList(Generic[T]):
    def __init__(
        self,
    ):
        self.__sentinel_head: DoublyLinkedNode[T] = DoublyLinkedNode[T]()
        self.__sentinel_tail: DoublyLinkedNode[T] = DoublyLinkedNode[T]()

        self.__sentinel_head.next_node = self.__sentinel_tail
        self.__sentinel_tail.previous_node = self.__sentinel_head

    def __repr__(self):
        node = self.__sentinel_head.next_node
        nodes = []
        while node != self.__sentinel_tail:
            nodes.append(node.__repr__())
            node = node.next_node
        return "sentinel_head<--->" + "<--->".join(nodes) + "<--->sentinel_tail"

    def __iter__(self):
        node = self.__sentinel_head.next_node
        while node != self.__sentinel_tail:
            yield node
            node = node.next_node

    def is_empty(self) -> bool:
        return self.__sentinel_head.next_node == self.__sentinel_tail

    def insert_before(self, node: DoublyLinkedNode[T], new_node: DoublyLinkedNode[T]):
        new_node.next_node = node
        new_node.previous_node = node.previous_node
        node.previous_node.next_node = new_node
        node.previous_node = new_node

    def insert_after(self, node: DoublyLinkedNode[T], new_node: DoublyLinkedNode[T]):
        new_node.previous_node = node
        new_node.next_node = node.next_node
        node.next_node.previous_node = new_node
        node.next_node = new_node

    def insert_beginning(self, new_node: DoublyLinkedNode[T]):
        self.insert_before(self.__sentinel_head.next_node, new_node)

    def insert_end(self, new_node: DoublyLinkedNode[T]):
        self.insert_after(self.__sentinel_tail.previous_node, new_node)

    def remove(self, node: DoublyLinkedNode[T]):
        node.previous_node.next_node = node.next_node
        node.next_node.previous_node = node.previous_node

    def pop(self):
        tail = self.__sentinel_tail.previous_node
        tail.previous_node.next_node = self.__sentinel_tail
        self.__sentinel_tail.previous_node = tail.previous_node

    def get_first(self) -> Optional[DoublyLinkedNode[T]]:
        return self.__sentinel_head.next_node if not self.is_empty() else None

    def get_last(self) -> Optional[DoublyLinkedNode[T]]:
        return self.__sentinel_tail.previous_node if not self.is_empty() else None

    def get_next(self, node: DoublyLinkedNode[T]) -> Optional[DoublyLinkedNode[T]]:
        next_node = node.next_node
        return next_node if next_node != self.__sentinel_tail else None

    def get_previous(self, node: DoublyLinkedNode[T]) -> Optional[DoublyLinkedNode[T]]:
        previous_node = node.previous_node
        return previous_node if previous_node != self.__sentinel_head else None

    def replace_node_with_tail(self, node: DoublyLinkedNode):
        tail = self.__sentinel_tail.previous_node
        second_last = tail.previous_node

        node.previous_node.next_node = tail
        tail.previous_node = node.previous_node

        if node == second_last:
            return

        tail.next_node = node.next_node
        node.next_node.previous_node = tail

        second_last.next_node = self.__sentinel_tail
        self.__sentinel_tail.previous_node = second_last


if __name__ == "__main__":
    dll = DoublyLinkedList()

    n1 = DoublyLinkedNode(data="node 1")
    n2 = DoublyLinkedNode(data="node 2")
    n3 = DoublyLinkedNode(data="node 3")
    n4 = DoublyLinkedNode(data="node 4")
    n5 = DoublyLinkedNode(data="node 5")

    dll.insert_beginning(n1)
    print(dll)
    dll.insert_beginning(n2)
    print(dll)
    dll.insert_end(n3)
    print(dll)
    dll.remove(n1)
    print(dll)
