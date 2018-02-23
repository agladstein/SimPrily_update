from sys import stderr
from sys import argv
import os.path
import linecache
import multiprocessing
import functools
from os import listdir
import csv
import re
import sh
from random import randint
import pandas as pd


def list_files(d):
    if os.path.exists(d):
        files = [os.path.join(d, f) for f in os.listdir(d)]
        return files
    else:
        print('{} does not exist'.format(d))
        exit()


def get_results_header(file_name):
    """
    Get the header line from a file
    :param path_sim_results: full or relative path to directory with simulation results files
    :param file_name: result file from one simulation
    :return: header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    """
    if os.path.isfile(file_name):
        header = linecache.getline(file_name, 1)
        return header
    else:
        print('{} does not exist'.format(file_name))


def col_num_equal(header, second_line):
    """
    Check if the two strings of the same number of lines
    :param header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    :param second_line: 2nd line of results file containing the parameter values and summary statistics
    :return: True or False
    """
    cols_header = len(header.split('\t'))
    cols_second_line = len(second_line.split('\t'))

    if cols_header == cols_second_line:
        return True
    else:
        return False


def get_second_line(file_name, header):
    """
    :param header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :param file_name: result file from one simulation
    :return: second_line: 2nd line of results file containing the parameter values and summary statistics 
    """

    if os.path.isfile(file_name):
        first_line = linecache.getline(file_name, 1)
        if header == first_line:
            second_line = linecache.getline(file_name, 2)
            return second_line


def combine_sim_results(path_sim_results, files_sim_results):
    """
    Combine the simulation results into one file.
    This function checks if headers match, and if the second line has the same number of columns as the header.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :return: Writes a new file called 'results_combined.txt' in the provided path.
    """

    if os.path.exists(path_sim_results):
        print('Combining simulation results into one file')

        header = get_results_header(files_sim_results[0])

        file_sim_combined_name = '{}/results_combined.txt'.format(path_sim_results)
        file_sim_combined = open(file_sim_combined_name, 'w')
        file_sim_combined.write(header)
        file_sim_combined.close()
        file_sim_combined = open(file_sim_combined_name, 'a')

        for file_name in files_sim_results:
            second_line = get_second_line(file_name, header)
            if second_line is not None and col_num_equal(header, second_line):
                file_sim_combined.write(second_line)

        file_sim_combined.close()

    else:
        print('{} does not exist'.format(path_sim_results))
        exit()

    return


def create_real_stats_file(files_sim_results, param_file):

    param_num = sum(1 for line in open(param_file))

    x = randint(0, len(files_sim_results))
    cross_val_file_name = files_sim_results[x]
    cross_val_df = pd.read_csv(cross_val_file_name, sep='\t')
    real_stats_df = cross_val_df.iloc[:, param_num:]

    return real_stats_df


def main():

    path_sim_results = argv[1]
    param_file = argv[2]

    files_sim_results = list_files(path_sim_results)
    combine_sim_results(path_sim_results, files_sim_results)
    real_stats_df = create_real_stats_file(files_sim_results, param_file)
    real_stats_file_name = '{}/results_real.txt'.format(path_sim_results)
    real_stats_df.to_csv(real_stats_file_name, sep='\t', index=False)

if __name__ == '__main__':
    main()
