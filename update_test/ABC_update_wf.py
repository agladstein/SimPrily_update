from sys import argv
from sys import executable
import os.path
import linecache
from random import randint
import pandas as pd
from collections import OrderedDict
import sh


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
    Get the second line from the simulation results file if header matches.
    :param file_name: result file from one simulation
    :param header: the header of one of the simulation results files in the directory. 
    This contains the names of the parameters and summary statistics.
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


def results_not_combined(path_run_ABC, files_sim_results):
    """
    Return false if the combined results file hasn't already been created or it doesn't have all of the simulations.
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :param files_sim_results: list of full paths of simulation results files.
    :return: True or False
    """

    file_sim_combined_name = '{}/results_combined.txt'.format(path_run_ABC)
    if os.path.isfile(file_sim_combined_name):
        sim_num = len(files_sim_results)
        line_num = sum(1 for line in open(file_sim_combined_name))
        if line_num >= sim_num:
            return False
        else:
            return True
    else:
        return True


def combine_sim_results(path_run_ABC, files_sim_results):
    """
    Combine the simulation results into one file.
    This function checks if headers match, and if the second line has the same number of columns as the header.
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :param files_sim_results: list of full paths of simulation results files.
    :return: Writes a new file called 'results_combined.txt' in the provided path.
    """

    if os.path.exists(path_run_ABC):
        print('Combining simulation results into one file')

        header = get_results_header(files_sim_results[0])

        file_sim_combined_name = '{}/results_combined.txt'.format(path_run_ABC)
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
        print('{} does not exist'.format(path_run_ABC))
        exit()

    return


def create_random_observed_df(files_sim_results):
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
    Get number of parameters and statistics from simulation.
    :param param_file: param file that was used to run the simulations.
    :param observed_df: dataframe of parameter and summary stats from one simulation. 
    :return: param_num: number of parameters
    :return: stats_num: number of stats
    """

    param_num = sum(1 for line in open(param_file))
    stats_num = len(observed_df.columns) - param_num
    return [param_num, stats_num]


def create_observed_stats_file(observed_df, param_num, path_run_ABC):
    """
    Create file of 'observed' stats from dataframe from one simulation. 
    :param observed_df: dataframe of parameter and summary stats from one simulation.
    :param param_num: number of parameters
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :return: observed_stats_df: dataframe of one randomly chosen simulation results file without the parameters.
    """

    observed_stats_df = observed_df.iloc[:, param_num:]

    observed_stats_file_name = '{}/results_observed.txt'.format(path_run_ABC)
    observed_param_stats_file_name = '{}/results_param_observed.txt'.format(path_run_ABC)
    observed_stats_df.to_csv(observed_stats_file_name, sep='\t', index=False)
    observed_df.to_csv(observed_param_stats_file_name, sep='\t', index=False)

    return


def run_PLS(path_run_ABC, param_num, stats_num):
    """
    Run R script to find PLS components.
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :param param_num: number of parameters
    :param stats_num: number of summary statistics
    :return: 
    """

    directory = '{}/'.format(path_run_ABC)
    filename = 'results_combined.txt'
    start_stats = param_num + 1
    end_stats = param_num + stats_num
    start_param = 1
    end_param = param_num
    # numComp = end_stats - start_stats
    numComp = 10

    if os.path.isfile('findPLS.r'):
        command = 'Rscript findPLS.r {} {} {} {} {} {} {}'.format(directory, filename, start_stats, end_stats, start_param, end_param, numComp)
        print(command)
        os.system(command)
    else:
        print('findPLS.r does not exist')
        exit()
    return


def create_ABC_PLS_trans_config(path_run_ABC, data_type):
    """
    Create ABCtoolbox config file to transform stats to PLS components.
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :param data_type: 'sim' or 'observed'
    :return: file_name: the name of the ABCtoolbox config file for PLS tranformation
    """

    if data_type == 'sim':
        base = 'results_combined'
        file_name = '{}/test_ABC_transform_sim.txt'.format(path_run_ABC)
    elif data_type == 'observed':
        base = 'results_observed'
        file_name = '{}/test_ABC_transform_observed.txt'.format(path_run_ABC)
    else:
        print('type must be sim or observed')
        exit()

    input = '{}/{}.txt'.format(path_run_ABC, base)
    output = '{}/{}_transformed.txt'.format(path_run_ABC, base)
    linearComb = '{}/Routput_results_combined.txt'.format(path_run_ABC, base)
    logfile = '{}/{}_transformed.log'.format(path_run_ABC, base)

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


def create_ABC_estimate_config(path_run_ABC, param_num):
    """
    Create ABCtoolbox config file for estimation.
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :param param_num: number of parameters
    :return: 
    """

    file_name = '{}/test_ABC_estimate.txt'.format(path_run_ABC)

    simName = '{}/results_combined_transformed.txt'.format(path_run_ABC)
    obsName = '{}/results_observed_transformed.txt'.format(path_run_ABC)
    params = '1-{}'.format(param_num)
    outputPrefix = '{}/ABC_update_estimate_10pls_100ret_'.format(path_run_ABC)
    logFile = '{}/ABC_update_estimate_10pls_100ret.log'.format(path_run_ABC)
    num_sims = sum(1 for line in open('{}/results_combined.txt'.format(path_run_ABC))) - 1

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
    config_file.write('maxReadSims {}\n'.format(num_sims))
    config_file.write('diracPeakWidth 0.01\n')
    config_file.write('posteriorDensityPoints 100\n')
    config_file.write('jointPosteriors A,B\n')
    config_file.write('jointPosteriorDensityPoints 100\n')
    config_file.write('writeRetained 0\n')
    config_file.write('outputPrefix {}\n'.format(outputPrefix))
    config_file.write('logFile {}\n'.format(logFile))
    config_file.write('verbose\n')

    config_file.close()
    return [file_name, outputPrefix]


def define_ABCtoolbox():
    """
    Define ABCtoolbox based on host
    :return: ABCtoolbox: path of ABCtoolbox
    """

    if os.path.isfile('/home/u15/agladstein/bin/ABCtoolbox_beta2'):
        ABCtoolbox = '/home/u15/agladstein/bin/ABCtoolbox_beta2'
    else:
        ABCtoolbox = './bin/ABCtoolbox'
    return ABCtoolbox


def run_ABCtoolbox(file_name, ABCtoolbox):
    """
    Run ABCtoolbox.
    :param file_name: ABCtoolbox config file
    :return: 
    """

    if os.path.isfile(file_name):
        command = '{} {}'.format(ABCtoolbox, file_name)
        print(command)
        os.system(command)
    else:
        print('{} does not exist'.format(file_name))
        exit()
    return


def create_param_dict(param_file_name, outputPrefix):
    """
    Create a dictionary with the parameters and file with posterior density
    :param param_file_name: original parameter file
    :param outputPrefix: prefix given in ABCtoolbox config file for estimation
    :return: param_dict: ordered dict with the parameters and file with posterior density
    """

    param_file = open(param_file_name, "r")
    param_dict = OrderedDict()
    for line in param_file:
        if "=" in line:
            param_dict[line.split("=")[0].strip()] = '{}model0_MarginalPosteriorDensities_Obs0.txt'.format(outputPrefix)
    param_file.close()
    return param_dict


def create_param_observed_dict(param_file_name, observed_df):
    """
    Create a dictionary with the parameters and file with posterior density
    :param param_file_name: original parameter file
    :param observed_df: dataframe of parameter and summary stats from one simulation.
    :return: param_observed_dict: ordered dict with the parameters and file with posterior density
    """

    param_file = open(param_file_name, "r")
    param_observed_dict = OrderedDict()
    for line in param_file:
        if "=" in line:
            param = line.split("=")[0].strip()
            param_observed_dict[param] = observed_df[param][0]
    param_file.close()
    return param_observed_dict


def create_param_file(param_dict, chrom, sim_type, obs):
    """
    Create new parameter file for simulations.    
    :param param_dict: ordered dict with the parameters and file with posterior density
    :param chrom: the chromosome number of the current chromosome
    :param sim_type: 'update' or 'observed'
    :param obs: number of observed iteration
    :return: 
    """

    input_dir = '{}/input_files'.format(os.path.dirname(os.path.realpath(argv[0])))

    if sim_type == 'update':
        new_param_file_name = '{}/param_chr{}.txt'.format(input_dir, chrom + 1)
    elif sim_type == 'observed':
        new_param_file_name = '{}/param_obs{}.txt'.format(input_dir, obs)

    try:
        os.remove(new_param_file_name)
    except OSError:
        pass
    new_param_file = open(new_param_file_name, 'a')

    for line in param_dict:
        new_param_file.write('{} = {}\n'.format(line, param_dict[line]))
    new_param_file.close()
    return


def sim_observed(path_run_ABC, obs, chrom):
    """
    Run simulation to create observed data based on observed parameter values from chr1.
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :param obs: number of observed iteration
    :param chrom: the chromosome number of the current chromosome
    :return: 
    """

    print('simulate based on observed parameter values from first chromosome')
    input_dir = '{}/input_files'.format(os.path.dirname(os.path.realpath(argv[0])))
    simprily_dir = os.path.dirname(os.path.dirname(os.path.realpath(argv[0])).rstrip('/'))
    script = '{}/simprily.py'.format(simprily_dir)
    p = '{}/param_obs{}.txt'.format(input_dir, obs)
    m = '{}/model_chr{}.csv'.format(input_dir, chrom)
    g = 'genetic_map_b37/genetic_map_GRCh37_chr{}.txt.macshs'.format(chrom)
    i = 'observed'
    o = path_run_ABC
    python = executable
    command = '{} {} -p {} -m {} -g {} -i {} -o {}'.format(python, script, p, m, g, i, o)
    os.system(command)
    return


def create_observed_df(path_run_ABC):
    """
    Create observed dataframe from simulated data from observed parameters
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :return: observed_df: dataframe of parameter and summary stats from one simulation.
    """

    observed_file_name = '{}/results/results_observed.txt'.format(path_run_ABC)
    observed_df = pd.read_csv(observed_file_name, sep='\t')
    return observed_df


def clean_sim_observed_out(path_run_ABC):
    """
    Clean up directory where simulation of observed data happened
    :param path_run_ABC: full or relative path to directory to run ABC in.
    :return: 
    """

    sh.rm('-r', '{}/germline_out'.format(path_run_ABC))
    sh.rm('-r', '{}/results'.format(path_run_ABC))
    sh.rm('-r', '{}/sim_data'.format(path_run_ABC))
    return


def main():

    path_sim = argv[1]
    param_file_name = argv[2]
    chrom = int(argv[3])
    obs = int(argv[4])
    path_sim_results = '{}/obs{}/chr{}/results'.format(path_sim, obs, chrom)
    path_run_ABC = '{}/obs{}/chr{}/ABC'.format(path_sim, obs, chrom)

    try:
        os.makedirs(path_run_ABC)
    except OSError:
        if not os.path.isdir(path_run_ABC):
            raise

    files_sim_results = list_files(path_sim_results)

    if results_not_combined(path_run_ABC, files_sim_results):
        combine_sim_results(path_run_ABC, files_sim_results)

    if chrom == 1:
        observed_df = create_random_observed_df(files_sim_results)
    else:
        sim_observed(path_run_ABC, obs, chrom)
        observed_df = create_observed_df(path_run_ABC)
        clean_sim_observed_out(path_run_ABC)

    param_observed_dict = create_param_observed_dict(param_file_name, observed_df)
    create_param_file(param_observed_dict, chrom, 'observed', obs)

    [param_num, stats_num] = get_param_stats_num(param_file_name, observed_df)

    create_observed_stats_file(observed_df, param_num, path_run_ABC)

    run_PLS(path_run_ABC, param_num, stats_num)

    ABCtoolbox = define_ABCtoolbox()

    ABC_PLS_trans_observed_file_name = create_ABC_PLS_trans_config(path_run_ABC, 'observed')
    run_ABCtoolbox(ABC_PLS_trans_observed_file_name, ABCtoolbox)

    ABC_PLS_trans_sim_file_name = create_ABC_PLS_trans_config(path_run_ABC, 'sim')
    run_ABCtoolbox(ABC_PLS_trans_sim_file_name, ABCtoolbox)

    [ABC_estimate_file_name, outputPrefix] = create_ABC_estimate_config(path_run_ABC, param_num)
    run_ABCtoolbox(ABC_estimate_file_name, ABCtoolbox)

    param_dict = create_param_dict(param_file_name, outputPrefix)
    create_param_file(param_observed_dict, chrom, 'update', obs)

if __name__ == '__main__':
    main()
