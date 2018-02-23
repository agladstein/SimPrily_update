from sys import stderr
from sys import argv
import os.path
import linecache
import multiprocessing
import functools
from os import listdir
import csv
import re


def get_results_header(path_sim_results, file_name):
    """
    Get the header line from a file
    :param path_sim_results: full or relative path to directory with simulation results files
    :param file_name: result file from one simulation
    :return: header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    """
    path_file_name = '{}/{}'.format(path_sim_results, file_name)
    if os.path.isfile(path_file_name):
        header = linecache.getline(path_file_name, 1)
    return header


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


def get_second_line(path_sim_results, file_name, header):
    """
    :param header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :param file_name: result file from one simulation
    :return: second_line: 2nd line of results file containing the parameter values and summary statistics 
    """
    path_file_name = '{}/{}'.format(path_sim_results, file_name)

    if os.path.isfile(path_file_name):
        first_line = linecache.getline(path_file_name, 1)
        if header == first_line:
            second_line = linecache.getline(path_file_name, 2)
            return second_line


def combine_sim_results(path_sim_results):
    """
    Combine the simulation results into one file.
    This function checks if headers match, and if the second line has the same number of columns as the header.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :return: Writes a new file called 'results_combined.txt' in the provided path.
    """

    if os.path.exists(path_sim_results):
        print('Combining simulation results into one file')

        files_sim_results = listdir(path_sim_results)
        header = get_results_header(path_sim_results, files_sim_results[0])

        file_sim_combined_name = '{}/results_combined.txt'.format(path_sim_results)
        file_sim_combined = open(file_sim_combined_name, 'w')
        file_sim_combined.write(header)
        file_sim_combined.close()
        file_sim_combined = open(file_sim_combined_name, 'a')

        for file_name in files_sim_results:
            second_line = get_second_line(path_sim_results, file_name, header)
            if second_line is not None and col_num_equal(header, second_line):
                file_sim_combined.write(second_line)

        file_sim_combined.close()

    else:
        print('{} does not exist'.format(path_sim_results))

    return


def main():

    sim_path_results = argv[1]

    combine_sim_results(sim_path_results)

if __name__ == '__main__':
    main()
