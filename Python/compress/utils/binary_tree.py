# coding: utf-8

from heapq import *


class Node(object):
    """ Node is an abstract class which represents a node in a BinaryTree.

    Attributes
    ----------
    value
        The value of the node
    left : Node
        The left child node.
    right : Node
        The right child node.
    """

    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

    def __str__(self):

        if self.is_leaf():
            return "[{}]".format(self.value)

        return "<{}> ( {} {} )".format(self.value, self.left, self.right)

    # Compares nodes between them : node1 < node2
    def __lt__(self, other):
        return self.value < other.value

    def is_leaf(self):
        return self.left is None and self.right is None


class BinaryTree(object):
    """Abstract binary tree class.

    Attributes
    ----------
    root_node : Node
        Root node of the tree.
    """
    def __init__(self):
        self.root_node = None

    def build_tree(self, values):

        heap = []

        for value in values:
            heappush(heap, value)

        while heap:  # While there are items to pop
            node1 = heappop(heap)  # will always exist

            try:
                node2 = heappop(heap)
                heappush(heap, self.create_node(node1, node2))

            # If node2 doesn't exist, it means the heap is empty and node1 is the final node
            except IndexError:
                self.root_node = node1

    def traversal_action(self, node):
        print(node.value)

    def inorder_traversal(self):

        heap = []
        current_node = self.root_node

        while heap or current_node is not None:
            if current_node is not None:
                heappush(heap, current_node)
                current_node = current_node.left
            else:
                current_node = heappop(heap)
                self.traversal_action(current_node)
                current_node = current_node.right

    def preorder_traversal(self):

        heap = []
        heappush(heap, self.root_node)

        while heap:  # While there are items to pop
            current_node = heappop(heap)

            self.traversal_action(current_node)

            if current_node.left is not None:
                heappush(heap, current_node.left)

            if current_node.right is not None:
                heappush(heap, current_node.right)

    def create_node(self, left=None, right=None):
        """ The value of the node depends on the algorithm, that's why this method must be overwritten.

        Parameters
        ----------
        left : Node
            The left node of the one we're creating.

        right : Node
            The right node of the one we're creating.

        Returns
        -------
        Node
            The newly created node.
        """
        raise NotImplemented("This method needs to be overwritten.")
