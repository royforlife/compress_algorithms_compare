# coding: utf-8


class LZW(object):
    """ Implementation of the LZW algorithm.

    Attributes
    ----------
    translation_dict : dict
        Association between repeated bytes sequences and integers.

    Examples
    --------
    An array of bytes like ['\x41', '\x42', '\x43', '\x0A', '\x00'] can be represented by an integer like 256.
    It means that one integer is able to represent multiple bytes at once.

    Notes
    -----
    On the internet we usually find this algorithm using integers that are coded on 12bits. But I think it's a waste of
    space and it can be optimized by sending along the encoded content, the size of the integers. So instead of sending
    12 bits integers, we will be able to send smaller (and bigger) integers. The size of the integers will be determined
    based on the biggest integer in the dictionary. This integer will be on 5 bits, it means other integers can be coded
    on 2^5 = 32 bits max. Which means the biggest supported dictionary is 2^32 = 4294967296 long. Which is more than
    enough.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.translation_dict = None
        self.max_size_integer_size = 5  # The integers size is encoded on 5 bits by default
        self.integers_size_bits = 0  # Max value must be 2**max_size_integer_size (= 32 by default)

    def __build_bytes_dictionary(self, decompression=False):
        if decompression:
            self.translation_dict = {byte: bytes([byte]) for byte in range(256)}
        else:
            self.translation_dict = {bytes([byte]): byte for byte in range(256)}

    def __compress(self, bytes_list):

        self.__build_bytes_dictionary()

        biggest_integer = 0
        compressed = []
        pattern = bytes([])

        for byte in bytes_list:
            byte_as_array = bytes([byte])
            current = pattern + byte_as_array

            if current in self.translation_dict:
                pattern = current
            else:
                self.translation_dict[current] = len(self.translation_dict)
                compressed.append(self.translation_dict[pattern])

                if biggest_integer < self.translation_dict[pattern]:
                    biggest_integer = self.translation_dict[pattern]

                pattern = byte_as_array

        compressed.append(self.translation_dict[pattern])

        if biggest_integer < self.translation_dict[pattern]:
            biggest_integer = self.translation_dict[pattern]

        if biggest_integer > 2 ** (2 ** self.max_size_integer_size):
            # Shouldn't happen
            raise ValueError("Can't encode such value... Maybe you should increase the size of max_size_integer_size.")

        self.integers_size_bits = biggest_integer.bit_length()

        if self.verbose:
            print("The biggest integer is {} so integers will be coded on {} bits.".format(biggest_integer,
                                                                                           self.integers_size_bits))
        return compressed

    def compress_file(self, input_filename, output_filename):
        with open(input_filename, "rb") as input_file:
            bytes_list = input_file.read()

        if not bytes_list:
            raise IOError("File is empty !")

        if self.verbose:
            print("Input size : {} bytes.".format(len(bytes_list)))

        compressed = self.__compress(bytes_list)

        if self.verbose:
            print("Assembling integers together...")

        # Originally, each integer was added to a big one using bits shifting, but this method was way to slow.
        # Strings are better for this purpose.
        binary_string_compressed = "1"  # Padding with a 1 to keep the first zeros when converting to integer

        # Add binary representation of the integers bit-length
        binary_string_compressed += format(self.integers_size_bits, "0{}b".format(self.max_size_integer_size))

        # https://waymoot.org/home/python_string/
        # According to this, the fastest way to concatenate strings is to use join() on a list
        bin_format = "0{}b".format(self.integers_size_bits)
        binary_string_compressed += ''.join([format(byte, bin_format) for byte in compressed])

        if self.verbose:
            print("Done.")

        big_int_compress = int(binary_string_compressed, 2)
        to_store_in_file = big_int_compress.to_bytes((big_int_compress.bit_length() + 7) // 8, 'big')

        total_file_size = len(to_store_in_file)

        if self.verbose:
            print("Output : {} bytes".format(total_file_size))

        if len(bytes_list) <= total_file_size:
            raise Exception("Aborted. No gain, you shouldn't compress that file. (+{} bytes)".format(
                total_file_size - len(bytes_list)))

        compression_rate = 100 - total_file_size * 100 / len(bytes_list)

        # Print anyway, even when not in verbose mode
        print("Compression gain : {0:.2f}%".format(compression_rate))

        with open(output_filename, "wb") as output_file:
            output_file.write(to_store_in_file)

        return compression_rate

    def __decompress(self, compressed_bytes_list):
        self.__build_bytes_dictionary(decompression=True)

        previous_code = compressed_bytes_list[0]
        decompressed = self.translation_dict[previous_code]

        first_byte = None

        for new_code in compressed_bytes_list[1:]:

            try:
                translation = self.translation_dict[new_code]
            except KeyError:
                translation = first_byte + self.translation_dict[previous_code]

            decompressed += translation

            first_byte = bytes([translation[0]])
            self.translation_dict[len(self.translation_dict)] = self.translation_dict[previous_code] + first_byte

            previous_code = new_code

        return decompressed

    def decompress_file(self, input_filename, output_filename):
        with open(input_filename, "rb") as input_file:
            bytes_list = input_file.read()

        if not bytes_list:
            raise IOError("File is empty !")

        big_int_compressed = int.from_bytes(bytes_list, 'big')
        bits_string_compressed = format(big_int_compressed, "0b")

        self.integers_size_bits = int(bits_string_compressed[1:self.max_size_integer_size + 1], 2)  # Skip first pad bit

        if self.verbose:
            print("Integers are {} bits long.".format(self.integers_size_bits))

        compressed = []

        for i in range(self.max_size_integer_size + 1, len(bits_string_compressed), self.integers_size_bits):
            compressed.append(int(bits_string_compressed[i:i + self.integers_size_bits], 2))

        decompressed = self.__decompress(compressed)

        with open(output_filename, "wb") as output_file:
            output_file.write(decompressed)
