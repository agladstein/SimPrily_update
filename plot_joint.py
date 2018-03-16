from sys import argv
import os
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def reformat_Characteristics(MarginalPosteriorCharacteristics_name):
    """
    reformat the ABCtoolbox output file MarginalPosteriorCharacteristics to a table with parameter as the rows and
     posterior density characteristics as columns.
    :param MarginalPosteriorCharacteristics_name: file name of ABCtoolbox output file with characteristics of posterior
    density.
    :return: df_table: pandas dataframe with parameters as rows and posterior density characteristics as columns
    """

    characteristics = ['mode', 'mean', 'median', 'q50_lower', 'q50_upper', 'q90_lower', 'q90_upper', 'q95_lower', 'q95_upper',
                  'q99_lower', 'q99_upper', 'HDI50_lower', 'HDI50_upper', 'HDI90_lower', 'HDI90_upper', 'HDI95_lower',
                  'HDI95_upper', 'HDI99_lower', 'HDI99_upper']
    n_chars = len(characteristics)

    if os.path.isfile(MarginalPosteriorCharacteristics_name):
        print('parsing {}'.format(MarginalPosteriorCharacteristics_name))

        df = pd.read_csv(MarginalPosteriorCharacteristics_name, sep = '\t').drop('dataSet', 1)
        header = list(df)

        df_list = []
        start = 0
        for i in range(1, int(len(df.columns)/n_chars)):
            param = header[start].split(characteristics[0])[0].strip('_')
            df_param = df.loc[:, header[start]:header[start + n_chars - 1]]
            df_param.columns = characteristics
            df_param['param'] = param
            df_param.set_index('param')
            df_list.append(df_param)
            start = n_chars * i
        df_table = pd.concat(df_list)

    else:
        print('{} does not exist'.format(MarginalPosteriorCharacteristics_name))
        exit()
    return df_table


def create_joint_df(jointPosterior_name):

    if os.path.isfile(jointPosterior_name):
        joint_B_A_df = pd.read_csv(jointPosterior_name, sep = '\t')
    else:
        print('{} does not exist'.format(jointPosterior_name))
        exit()
    return joint_B_A_df


def plot_joint_mtpltlb(jointPosterior_name, df_chrs_reformat, results_param_observed):

    tbl = np.genfromtxt(jointPosterior_name, names=True)

    # density map
    A, B, z = tbl['A'], tbl['B'], tbl['density']
    A = np.unique(A)
    B = np.unique(B)
    X, Y = np.meshgrid(A, B)
    Z = z.reshape(len(B), len(A))
    plt.pcolormesh(X, Y, Z, cmap='viridis')
    colorbar = plt.colorbar()
    colorbar.set_label('Density')

    # y = x line
    plt.plot(A, A, color='black')

    # Scatterplot point
    B_mode = df_chrs_reformat.loc[df_chrs_reformat['param'] == 'B']['mode']
    A_mode = df_chrs_reformat.loc[df_chrs_reformat['param'] == 'A']['mode']
    plt.scatter(A_mode, B_mode, marker='*', facecolor='black', edgecolor='none')
    
    tbl_true = np.genfromtxt(results_param_observed, names=True)
    A_true, B_true = tbl_true['A'], tbl_true['B']
    plt.scatter(A_true, B_true, marker='+', facecolor='black', edgecolor='none')
    
    # Axes limits and labels
    plt.xlim(np.min(A), np.max(A))
    plt.xlabel('A')

    plt.ylabel('B')
    plt.ylim(np.min(B), np.max(B))

    plot_name = '{}.png'.format(jointPosterior_name.strip(''))
    plt.savefig(plot_name)

    return


def main():
    jointPosterior_name = argv[1]
    MarginalPosteriorCharacteristics_name = argv[2]
    results_param_observed = argv[3]
    
    df_chrs_reformat = reformat_Characteristics(MarginalPosteriorCharacteristics_name)
    joint_B_A_df = create_joint_df(jointPosterior_name)
    plot_joint_mtpltlb(jointPosterior_name, df_chrs_reformat, results_param_observed)

if __name__ == '__main__':
    main()