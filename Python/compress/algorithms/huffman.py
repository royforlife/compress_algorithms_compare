# coding: utf-8

from compress.utils.binary_tree import *


class HuffmanNode(Node):
    """Unlike the classic Node, the HuffmanNode is sorted by frequency and not value.

    Attributes
    ----------
    frequency : int
        Holds the frequency of the byte(s).

    """

    def __init__(self, frequency=0, value=None):
        super().__init__(value)
        self.frequency = frequency

    def __lt__(self, other):
        return self.frequency < other.frequency

    def __str__(self):
        if self.is_leaf():
            return "[{}]".format(self.value)

        return "<{}> ( {} {} )".format(self.frequency, self.left, self.right)


class Huffman(BinaryTree):
    """ This class is an implementation of the Huffman compression algorithm.

    Attributes
    ----------
    bytes_occurrences : dict
        Association between a byte and its number occurrences.

    huffman_code : dict
        Association between a byte and its new code.

    encoded_tree : str
        Contains the tree in a minimalist representation. This is a binary string that will be converted

    Notes
    -----
    The method we have chosen to use here is semi-adaptive because it will build a tree based on actual frequencies
    instead of using static symbols weights.
    (but it will not dynamically change the tree like the real adaptive algorithm
    https://en.wikipedia.org/wiki/Adaptive_Huffman_coding ).
    The problem with this method is that we have to transmit the tree with the encoded content in order to decompress.
    The tree can't be bigger than 256 leaves, which means this method will be good to compress big chunks of data but
    it will be inefficient to compress small ones.
    """

    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.bytes_occurrences = {}
        self.huffman_code = {}
        self.encoded_tree = None

    def create_node(self, left=None, right=None):
        """ Redefine parent's behavior.

        Notes
        -----
        Our algorithm only cares about tree leaves but we need the tree to be built depending on bytes occurrences,
        that why newly created node's value will be an addition of children sort_on values (which are in this algorithm
        byte occurrences).
        """

        new_node = HuffmanNode(0 if left is None or right is None else left.frequency + right.frequency)
        new_node.left = left
        new_node.right = right
        return new_node

    def traversal_action(self, node):
        """Overwrites BinaryTree's default action.
        In huffman, the traversal enables the creation of a binary minimalist representation of the tree in order
        to store the tree space-efficiently.

        Parameters
        ----------
        node : Node
            The node to process.
        """

        if node.is_leaf():
            self.encoded_tree += "1" + format(node.value, "08b")
        else:
            self.encoded_tree += "0"

    def __find_bytes_occurrences(self, bytes_list):

        self.bytes_occurrences.clear()

        # Count bytes
        for byte in bytes_list:
            try:
                self.bytes_occurrences[byte] += 1
            except KeyError:
                self.bytes_occurrences[byte] = 1

    def __create_huffman_code(self, node, code=""):

        if node.is_leaf():
            self.huffman_code[node.value] = code

        else:
            self.__create_huffman_code(node.left, code + "0")
            self.__create_huffman_code(node.right, code + "1")

    def build_tree_from(self, binary_string):
        """ Recreates the tree when minimized by the traversal_actions and stored to a file.

        Attributes
        ----------
        binary_string : str
            Contains the bits from the whole file.
        """
        self.root_node = self.create_node()
        self.root_node.value = 0
        return self.__build_tree_from(binary_string, self.root_node)

    def __build_tree_from(self, binary_string, current_node, current_index=0):
        current_node.left = self.create_node()
        current_node.right = self.create_node()

        bit = binary_string[current_index]

        if bit == "1":
            # We grab the 8 bits following the 1
            current_node.left.value = int(binary_string[current_index + 1:current_index + 1 + 8], 2)
            current_index += 9  # Skip the 1 and the 8 following bits

        else:
            current_node.left.value = 0
            current_index = self.__build_tree_from(binary_string, current_node.left, current_index+1)

        bit = binary_string[current_index]

        if bit == "1":
            # We grab the 8 bits following the 1
            current_node.right.value = int(binary_string[current_index + 1:current_index + 1 + 8], 2)
            current_index += 9  # Skip the 1 and the 8 following bits
        else:
            current_node.right.value = 0
            current_index = self.__build_tree_from(binary_string, current_node.right, current_index+1)

        return current_index

    def __compress(self, bytes_list):

        self.__find_bytes_occurrences(bytes_list)

        if self.verbose:
            print("Occurrences: " + str(self.bytes_occurrences))
            print("Number of different bytes : {}".format(len(self.bytes_occurrences)))

        self.build_tree([HuffmanNode(self.bytes_occurrences[byte], byte) for byte in self.bytes_occurrences])

        if self.verbose:
            print("Tree: " + str(self.root_node))

        self.__create_huffman_code(self.root_node)

        if self.verbose:
            print("Code: " + str(self.huffman_code))

        encoded_string = "1"  # Padding needed to convert to bytes, otherwise we will lose information (the first zeros)

        for byte in bytes_list:
            encoded_string += self.huffman_code[byte]

        # Convert to bytes array
        return int(encoded_string, 2).to_bytes((len(encoded_string) + 7) // 8, byteorder='big')

    def compress_file(self, input_filename, output_filename):

        if self.verbose:
            print("Reading {}...".format(input_filename))

        with open(input_filename, "rb") as input_file:
            bytes_list = input_file.read()  # All the file will be in memory, can be a problem with huge files.

        if not bytes_list:
            raise IOError("File is empty !")

        if self.verbose:
            print("Input size : ", len(bytes_list))

        compressed = self.__compress(bytes_list)

        if self.verbose:
            print("Compressed size : ", len(compressed))

        # There is a maximum of 256 leaves in the tree (because there are 256 different bytes), so the number of leaves
        # in the tree will be encoded on 1 byte. A byte can be any value between 0 and 255. And the maximum number of
        # leaves is 256. So we will store size-1. It's not a problem because the tree can't contain 0 leaf.
        self.encoded_tree = ""  # Reset encoded tree
        self.preorder_traversal()

        # Pad with a 1 to keep zeros
        self.encoded_tree = "1" + self.encoded_tree[1:]  # Remove the 0 of the root node which is useless, 1 bit gain :)

        tree_big_int_format = int(self.encoded_tree, 2)
        final_encoded_tree = tree_big_int_format.to_bytes((tree_big_int_format.bit_length() + 7) // 8, 'big')

        if self.verbose:
            print("final_encoded_tree = ", final_encoded_tree)

        total_file_size = len(final_encoded_tree) + len(compressed)

        if self.verbose:
            print("Total size output : {} bytes".format(total_file_size))

        if len(bytes_list) <= total_file_size:
            raise Exception("Aborted. No gain, you shouldn't compress that file. (+{} bytes)".format(
                total_file_size - len(bytes_list)))

        compression_rate = 100 - total_file_size * 100 / len(bytes_list)

        # Print anyway, even when not in verbose mode
        print("Compression gain : {0:.2f}%".format(compression_rate))

        with open(output_filename, "wb") as output_file:
            output_file.write(final_encoded_tree)
            output_file.write(compressed)

        return compression_rate

    def __decompress(self, compressed_data_bits):

        decompressed = []
        current_node = self.root_node

        for i in compressed_data_bits:

            if current_node.is_leaf():
                decompressed.append(current_node.value)
                current_node = self.root_node

            if i == "0":
                current_node = current_node.left

            elif i == "1":
                current_node = current_node.right

        return bytes(decompressed)

    def decompress_file(self, input_filename, output_filename):

        with open(input_filename, "rb") as input_file:
            bytes_list = input_file.read()  # All the file will be in memory, can be a problem with huge files.

        if not bytes_list:
            raise IOError("File is empty !")

        binary_string = ""

        for byte in bytes_list:
            binary_string += format(byte, "08b")

        padding_index = 0
        while binary_string[padding_index] == "0":
            padding_index += 1

        binary_string = binary_string[padding_index+1:]  # Remove first zeros and the 1 padding
        tree_end_index = self.build_tree_from(binary_string)
        binary_string = binary_string[tree_end_index:]

        if self.verbose:
            print("Rebuilt tree: ", self.root_node)

        padding_index = 0
        while binary_string[padding_index] == "0":
            padding_index += 1

        binary_string = binary_string[padding_index + 1:]  # Remove first zeros and the 1 padding

        decompressed = self.__decompress(binary_string)

        with open(output_filename, "wb") as output_file:
            output_file.write(decompressed)
