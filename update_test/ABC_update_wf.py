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
import subprocess


def list_files(d):
    """
    list full paths of files in directory
    :param d: path to directory 
    :return: list of files
    """
    if os.path.exists(d):
        files = [os.path.join(d, f) for f in os.listdir(d)]
        return files
    else:
        print('{} does not exist'.format(d))
        exit()


def get_results_header(file_name):
    """
    Get the header line from a file
    :param file_name: result file from one simulation
    :return: header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    """

    if os.path.isfile(file_name):
        header = linecache.getline(file_name, 1)
        return header
    else:
        print('{} does not exist'.format(file_name))
        exit()


def get_second_line(file_name, header):
    """
    :param header: the header of one of the simulation results files in the directory.
    This contains the names of the parameters and summary statistics.
    :param file_name: result file from one simulation
    :return: second_line: 2nd line of results file containing the parameter values and summary statistics 
    """

    if os.path.isfile(file_name):
        first_line = linecache.getline(file_name, 1)
        if header == first_line:
            second_line = linecache.getline(file_name, 2)
            return second_line
    return None


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


def combine_sim_results(path_sim_results, files_sim_results):
    """
    Combine the simulation results into one file.
    This function checks if headers match, and if the second line has the same number of columns as the header.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :param files_sim_results: list of full paths of simulation results files.
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


def create_observed_df(files_sim_results):
    """
    Randomly pick simulation to use as observed data.
    :param files_sim_results: list of full paths of simulation results files.
    :return: observed_df: dataframe of parameter and summary stats from one simulation.
    """

    x = randint(0, len(files_sim_results))
    observed_file_name = files_sim_results[x]
    observed_df = pd.read_csv(observed_file_name, sep='\t')

    return observed_df


def get_param_stats_num(param_file, observed_df):
    """

    :param param_file: param file that was used to run the simulations.
    :return: 
    """

    param_num = sum(1 for line in open(param_file))
    stats_num = len(observed_df.columns) - param_num
    return [param_num, stats_num]


def create_observed_stats_file(observed_df, param_num, path_sim_results):
    """
    
    :param observed_df: dataframe of parameter and summary stats from one simulation.
    :param param_num: number of parameters
    :param path_sim_results: full or relative path to directory with simulation results files.
    :return: observed_stats_df: dataframe of one randomly chosen simulation results file without the parameters.
    """

    observed_stats_df = observed_df.iloc[:, param_num:]

    observed_stats_file_name = '{}/results_observed.txt'.format(path_sim_results)
    observed_param_stats_file_name = '{}/results_param_observed.txt'.format(path_sim_results)
    observed_stats_df.to_csv(observed_stats_file_name, sep='\t', index=False)
    observed_df.to_csv(observed_param_stats_file_name, sep='\t', index=False)

    return


def run_PLS(path_sim_results, param_num, stats_num):
    """
    Run R script to find PLS components.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :param param_num: number of parameters
    :param stats_num: number of summary statistics
    :return: 
    """

    directory = '{}/'.format(path_sim_results)
    filename = 'results_combined.txt'
    start_stats = param_num + 1
    end_stats = param_num + stats_num
    start_param = 1
    end_param = param_num
    # numComp = end_stats - start_stats
    numComp = 10

    print('Rscript', 'findPLS.r', directory, filename, start_stats, end_stats, start_param, end_param, numComp)
    return


def create_ABC_PLS_trans_config(path_sim_results, data_type):
    """
    Create ABCtoolbox config file to transform stats to PLS components.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :param data_type: 'sim' or 'observed'
    :return: 
    """

    if data_type == 'sim':
        base = 'results_combined'
        file_name = '{}/test_ABC_transform_sim.txt'.format(path_sim_results)
    elif data_type == 'observed':
        base = 'results_observed'
        file_name = '{}/test_ABC_transform_observed.txt'.format(path_sim_results)
    else:
        print('type must be sim or observed')
        exit()

    input = '{}/{}.txt'.format(path_sim_results, base)
    output = '{}/{}_transformed.txt'.format(path_sim_results, base)
    linearComb = '{}/Routput_{}.txt'.format(path_sim_results, base)
    logfile = '{}/{}_transformed.log'.format(path_sim_results, base)

    try:
        os.remove(file_name)
    except OSError:
        pass
    config_file = open(file_name, 'a')

    config_file.write('task transform\n')
    config_file.write('input {}\n'.format(input))
    config_file.write('output {}\n'.format(output))
    config_file.write('linearComb {}\n'.format(linearComb))
    config_file.write('boxcox 1\n')
    config_file.write('logFile {}\n'.format(logfile))
    config_file.write('verbose\n')

    config_file.close()
    return file_name


def run_ABC_transform(file_name):
    """
    Run ABCtoolbox to transform the summary statistics to PLS components.
    :param file_name: ABCtoolbox config file
    :return: 
    """

    if os.path.isfile(file_name):
        if os.path.isfile('./bin/ABCtoolbox'):
            command = './bin/ABCtoolbox {}'.format(file_name)
            print(command)
            os.system(command)
        else:
            print('./bin/ABCtoolbox does not exist')
            exit()
    else:
        print('{} does not exist'.format(file_name))
        exit()
    return


def create_ABC_estimate_config(path_sim_results, param_num):
    """
    Create ABCtoolbox config file for estimation.
    :param path_sim_results: full or relative path to directory with simulation results files.
    :param param_num: number of parameters
    :return: 
    """

    file_name = '{}/test_ABC_estimate.txt'.format(path_sim_results)

    simName = '{}/results_combined_transformed.txt'.format(path_sim_results)
    obsName = '{}/results_observed_transformed.txt'.format(path_sim_results)
    params = '1-{}'.format(param_num)
    outputPrefix = '{}/ABC_update_estimate_10pls_100ret_'.format(path_sim_results)
    logFile = '{}/ABC_update_estimate_10pls_100ret.log'.format(path_sim_results)

    try:
        os.remove(file_name)
    except OSError:
        pass
    config_file = open(file_name, 'a')

    config_file.write('task estimate\n')
    config_file.write('simName {}\n'.format(simName))
    config_file.write('obsName {}\n'.format(obsName))
    config_file.write('params {}\n'.format(params))
    config_file.write('numRetained 100\n')
    config_file.write('diracPeakWidth 0.01\n')
    config_file.write('posteriorDensityPoints 100\n')
    config_file.write('jointPosteriors A,B\n')
    config_file.write('jointPosteriorDensityPoints 100\n')
    config_file.write('writeRetained 0\n')
    config_file.write('outputPrefix {}\n'.format(outputPrefix))
    config_file.write('logFile {}\n'.format(logFile))
    config_file.write('verbose\n')

    config_file.close()
    return file_name


def main():

    path_sim_results = argv[1]
    param_file = argv[2]

    files_sim_results = list_files(path_sim_results)

    combine_sim_results(path_sim_results, files_sim_results)

    observed_df = create_observed_df(files_sim_results)

    [param_num, stats_num] = get_param_stats_num(param_file, observed_df)

    create_observed_stats_file(observed_df, param_num, path_sim_results)

    run_PLS(path_sim_results, param_num, stats_num)

    ABC_PLS_trans_observed_file_name = create_ABC_PLS_trans_config(path_sim_results, 'observed')
    ABC_PLS_trans_sim_file_name = create_ABC_PLS_trans_config(path_sim_results, 'sim')

    run_ABC_transform(ABC_PLS_trans_observed_file_name)
    run_ABC_transform(ABC_PLS_trans_sim_file_name)

    ABC_estimate_file_name = create_ABC_estimate_config(path_sim_results, param_num)

if __name__ == '__main__':
    main()
