#!/usr/bin/python3
# coding: utf-8

from optparse import OptionParser
from compress.algorithms.huffman import Huffman
from compress.algorithms.lzw import LZW
import os
import time
import matplotlib.pyplot as plt
import numpy as np


def benchmark():
    print("Benchmark starting...")

    images_count = 14

    huffman_times = []
    lzw_times = []
    huffman_compression_rates = []
    lzw_compression_rates = []

    for i in range(1, images_count + 1):
        input_filename = "dataset/image{}.ppm".format(i)
        output_filename = "dataset/image{}.ppm.tor".format(i)

        print("Benchmarking Huffman...")
        begin = time.time()
        compression_rate = Huffman(verbose=False).compress_file(input_filename, output_filename)
        time_result = time.time() - begin
        print("Done in {0:.2f}s\n".format(time_result))
        huffman_times.append(time_result)
        huffman_compression_rates.append(compression_rate)

        print("Benchmarking LZW...")
        begin = time.time()
        compression_rate = LZW(verbose=False).compress_file(input_filename, output_filename)
        time_result = time.time() - begin
        print("Done in {0:.2f}s\n".format(time_result))
        lzw_times.append(time_result)
        lzw_compression_rates.append(compression_rate)

        os.remove(output_filename)

    bar_width = 0.35

    fig, ax = plt.subplots()
    index = np.arange(images_count)
    ax.bar(index, huffman_times, bar_width, color='b', label='Huffman', alpha=0.4)
    ax.bar(index + bar_width, lzw_times, bar_width, color='r', label='LZW', alpha=0.4)
    ax.set_xlabel('Image Number')
    ax.set_ylabel('Speed (s)')
    ax.set_title('Algorithms speed')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels([str(i) for i in range(1, images_count + 1)])
    ax.legend()
    fig.tight_layout()

    fig, ax = plt.subplots()
    ax.bar(index, huffman_compression_rates, bar_width, color='b', label='Huffman', alpha=0.4)
    ax.bar(index + bar_width, lzw_compression_rates, bar_width, color='r', label='LZW', alpha=0.4)
    ax.set_xlabel('Image Number')
    ax.set_ylabel('Compression rate (%)')
    ax.set_title('Algorithms compression')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels([str(i) for i in range(1, images_count + 1)])
    ax.legend()
    fig.tight_layout()

    plt.show()


if __name__ == "__main__":

    parser = OptionParser(usage="Usage: %prog [options] file")
    parser.set_defaults(verbose=False, compress=True, algo="lzw")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Set verbose mode to understand what's underneath.")

    parser.add_option("-a", "--algo", action="store", dest="algo",
                      help="Set the algorithm you want to use (Huffman or LZW) default is LZW.")

    parser.add_option("-o", "--output", action="store", dest="output",
                      help="Set the output file name, default is the same as input + tor extension.")

    parser.add_option("-d", "--decompress", action="store_false", dest="compress",
                      help="Decompress the file.")

    parser.add_option("--benchmark", action="store_true", dest="benchmark",
                      help="Start benchmarking compession algorithms.")

    (options, args) = parser.parse_args()

    if options.benchmark:
        benchmark()
        exit()

    if len(args) != 1:
        parser.error("Please specify a file to compress.")

    if os.path.isdir(args[0]):
        parser.error("This program doesn't support directory compressing yet.")

    if options.output is None:
        if options.compress:
            options.output = args[0] + ".tor"
        else:
            tor_index = args[0].find(".tor")

            if tor_index != -1:
                options.output = args[0][:tor_index]
            else:
                options.output = args[0] + "_extracted"

    algo = None

    if options.algo.lower() == "huffman":
        algo = Huffman(verbose=options.verbose)
    elif options.algo.lower() == "lzw":
        algo = LZW(verbose=options.verbose)
    else:
        parser.error("Algorithm does not exist or is not supported yet.")

    if options.compress:
        algo.compress_file(args[0], options.output)
    else:
        algo.decompress_file(args[0], options.output)
