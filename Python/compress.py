#!/usr/bin/python3
# coding: utf-8

from optparse import OptionParser
from compress.algorithms.huffman import Huffman
from compress.algorithms.lzw import LZW
import os
import time
import pandas
import matplotlib.pyplot as plt
import numpy as np
import energyusage

def lzw():
    lzw_df = pandas.DataFrame(columns=["compress_rate", "time", "energy"], index=["txt", "image", "video", "excel"])
    for type in ["txt"]:
        path = "./compress/dataset/" + type
        input_path = path + "/input"
        output_path = path + "/output" + "/lzw"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for filename in os.listdir(input_path):
            input_file = input_path + "/" + filename
            output_file = output_path + "/" + filename + ".tor"
            print("input_file: ", input_file)
            print("output_file: ", output_file)
            begin = time.time()
            lzw_compression_rate = LZW(verbose=False).compress_file(input_file, output_file)
            lzw_time = time.time() - begin
            lzw_energy = 0
            lzw_df.loc[type] = [lzw_compression_rate, lzw_time, lzw_energy]
    print("lzw_df: \n", lzw_df)
    lzw_df.to_csv("./compress/result/benchmark/lzw.csv")
    return True

def huffman():
    huffman_df = pandas.DataFrame(columns=["compress_rate", "time", "energy"], index=["txt", "image", "video", "excel"])
    for type in ["txt"]:
        path = "./compress/dataset/" + type
        input_path = path + "/input"
        output_path = path + "/output" + "/huffman"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for filename in os.listdir(input_path):
            input_file = input_path + "/" + filename
            output_file = output_path + "/" + filename + ".tor"
            print("input_file: ", input_file)
            print("output_file: ", output_file)
            begin = time.time()
            huffman_compression_rate = Huffman(verbose=False).compress_file(input_file, output_file)
            huffman_time = time.time() - begin
            huffman_energy = 0
            huffman_df.loc[type] = [huffman_compression_rate, huffman_time, huffman_energy]
    print("huffman_df: \n", huffman_df)
    huffman_df.to_csv("./compress/result/benchmark/huffman.csv")
    return True

def benchmark():
    print("Benchmark starting...")
    lzw()
    huffman()
    # run_time_lzw, energy_lzw, _ = energyusage.evaluate(lzw)
    # run_time_huffman, energy_lzw_huffman, _ = energyusage.evaluate(huffman)
    # print("run_time_lzw: ", run_time_lzw, "energy_lzw: ", energy_lzw)
    # print("run_time_huffman: ", run_time_huffman, "energy_lzw_huffman: ", energy_lzw_huffman)
    images_count = 1

    huffman_times = []
    lzw_times = []
    huffman_compression_rates = []
    lzw_compression_rates = []



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
