import pandas as pd
from ggplot import *
import numpy as np
import os
from sys import argv


def calc_estimate_dist(param, combined_PosteriorCharacteristics_observed_df):
    estimate = '{}_mode'.format(param)
    estimate_dist_name = '{}_estimate_dist'.format(param)
    combined_PosteriorCharacteristics_observed_df[estimate_dist_name] = (combined_PosteriorCharacteristics_observed_df[estimate] - combined_PosteriorCharacteristics_observed_df[param]) ** 2
    return combined_PosteriorCharacteristics_observed_df


def calc_HPDI_dist(param, combined_PosteriorCharacteristics_observed_df):
    HDI95_upper_name = '{}_HDI95_upper'.format(param)
    HDI95_lower_name = '{}_HDI95_lower'.format(param)
    HPDI_dist_name = '{}_HPDI_dist'.format(param)
    HDI95_upper = combined_PosteriorCharacteristics_observed_df[HDI95_upper_name]
    HDI95_lower = combined_PosteriorCharacteristics_observed_df[HDI95_lower_name]
    true = combined_PosteriorCharacteristics_observed_df[param]

    combined_PosteriorCharacteristics_observed_df[HPDI_dist_name] = np.where(
        (true < HDI95_lower) & (true > HDI95_upper), ((true - HDI95_lower) ** 2 + (true - HDI95_upper) ** 2) * (-1),
        (true - HDI95_lower) ** 2 + (true - HDI95_upper) ** 2)
    return combined_PosteriorCharacteristics_observed_df


def proportion_smaller_chr1(df, column, chrom):
    chr1 = df[column].loc[(df['chr'] == '1')].reset_index(drop=True)
    other_chr = df[column].loc[(df['chr'] == str(chrom))].reset_index(drop=True)

    proportion = (float(sum(chr1 > other_chr) - sum(chr1 < 0)))/100
    return proportion


def boxplot_estimate_dist(param, combined_PosteriorCharacteristics_observed_df, y_axis_name):
    plot = ggplot(aes(x = 'chr', y = y_axis_name), data = combined_PosteriorCharacteristics_observed_df) + \
        geom_boxplot() + \
        theme_bw()
    return plot


def lineplot_estimate_dist(param, combined_PosteriorCharacteristics_observed_df, y_axis_name):
    plot = ggplot(aes(x = 'chr', y = y_axis_name, colour='obs'), data = combined_PosteriorCharacteristics_observed_df) + \
        geom_point() + \
        geom_line() + \
        theme_bw()
    return plot


def density_plot(param, PosteriorDensities_df, true_value):
    density = list(PosteriorDensities_obs1_df)[PosteriorDensities_obs1_df.columns.get_loc(param)+1]
    plot = ggplot(aes(x = param, y = density, colour = 'chr'), data = PosteriorDensities_df) + \
        geom_line(size = 2) + \
        geom_vline(x = true_value, size = 3, colour = 'black') + \
        scale_color_brewer(type='div', palette=2) + \
        theme_bw()
    return plot


def main():
    combined_PosteriorCharacteristics_observed_name = argv[1]
    combined_PosteriorDensities_name = argv[2]

    combined_PosteriorCharacteristics_observed_df = pd.read_csv(combined_PosteriorCharacteristics_observed_name, sep='\t')
    combined_PosteriorDensities_df = pd.read_csv(combined_PosteriorDensities_name, sep='\t')
    combined_PosteriorCharacteristics_observed_df['obs'] = combined_PosteriorCharacteristics_observed_df['obs'].astype(str)
    combined_PosteriorDensities_df['obs'] = combined_PosteriorDensities_df['obs'].astype(str)
    combined_PosteriorCharacteristics_observed_df['chr'] = combined_PosteriorCharacteristics_observed_df['chr'].astype(str)
    combined_PosteriorDensities_df['chr'] = combined_PosteriorDensities_df['chr'].astype(str)

    parameters = list(combined_PosteriorCharacteristics_observed_df)[0:7]
    for param in parameters:
        combined_PosteriorCharacteristics_observed_df = calc_estimate_dist(param,combined_PosteriorCharacteristics_observed_df)
        combined_PosteriorCharacteristics_observed_df = calc_HPDI_dist(param,combined_PosteriorCharacteristics_observed_df)

        estimate_dist_name = '{}_estimate_dist'.format(param)
        HPDI_dist_name = '{}_HPDI_dist'.format(param)
        proportion_smaller_estimate_dist = []
        proportion_smaller_HPDI_dist = []
        for chrom in range(2, 11):
            proportion_smaller_estimate_dist.append(proportion_smaller_chr1(combined_PosteriorCharacteristics_observed_df, estimate_dist_name, str(chrom)))
            proportion_smaller_HPDI_dist.append(proportion_smaller_chr1(combined_PosteriorCharacteristics_observed_df, HPDI_dist_name, str(chrom)))

    print('done')

if __name__ == '__main__':
    main()
