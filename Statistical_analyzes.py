import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats
import numpy as np
import warnings
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def lcs():
    variant_num = 'ELE-3'
    fitness_threshold = False
    fitness_duration = 1
    fitness_lcs = 0
    constraints = 60
    lcs_results = pd.read_csv('run_lcs_07Jun.csv')

    data = lcs_results.loc[
        (lcs_results['variant_num'] == variant_num) & (lcs_results['fitness_threshold'] == fitness_threshold) & (
                lcs_results['fitness_duration'] == float(fitness_duration)) &
        (lcs_results['fitness_lcs'] == float(fitness_lcs)) &
        (lcs_results['success'] == 1) & (lcs_results['% constraints'] == int(constraints))]

    print(data.shape)
    print("count TRUE", data['is_seq_valid'].value_counts())
    mean_p = (data['% similar_to_expert'] / data['length']).mean()
    print(" % similar to expert, ", mean_p)


def csp_mean():
    run_results = pd.read_csv('run_lcs_07Jun.csv')
    var = 'ELE-1'
    data_csp = run_results.loc[
        (run_results['variant_num'] == var) & (
                run_results['algorithm'] == 'CSP') & run_results['success'] == 1]
    data_random = run_results.loc[
        (run_results['variant_num'] == var) & (
                run_results['algorithm'] == 'Random') & run_results['success'] == 1]
    print(data_csp.shape)
    print(data_random.shape)
    print(data_csp['initial_pop_runtime'].mean())
    print(data_random['initial_pop_runtime'].mean())


def csp_prepare_to_regression():
    """ CSP regression"""
    run_100 = pd.read_csv('run_csp - FINAL.csv')[['variant_num', 'algorithm', 'initial_pop_runtime']]
    run_100['constraints'] = 100
    run_100['chromo_length'] = None
    run_60 = pd.read_csv('run_csp_60_constraints.csv')[['variant_num', 'algorithm', 'initial_pop_runtime']]
    run_60['constraints'] = 60
    run_60['chromo_length'] = None
    run_20 = pd.read_csv('run_csp_20_constraints.csv')[['variant_num', 'algorithm', 'initial_pop_runtime']]
    run_20['constraints'] = 20
    run_20['chromo_length'] = None

    data_union = pd.concat([run_100, run_60, run_20])

    data_union.loc[data_union.variant_num == "MDC-1", "chromo_length"] = 7
    data_union.loc[data_union.variant_num == "MDC-2", "chromo_length"] = 8
    data_union.loc[data_union.variant_num == "MDC-3", "chromo_length"] = 7
    data_union.loc[data_union.variant_num == "KTR-1", "chromo_length"] = 5
    data_union.loc[data_union.variant_num == "KTR-2", "chromo_length"] = 5
    data_union.loc[data_union.variant_num == "KTR-3", "chromo_length"] = 5
    data_union.loc[data_union.variant_num == "ELE-1", "chromo_length"] = 12
    data_union.loc[data_union.variant_num == "ELE-2", "chromo_length"] = 32
    data_union.loc[data_union.variant_num == "ELE-3", "chromo_length"] = 13

    X = pd.DataFrame(data_union, columns=['algorithm', 'constraints', 'chromo_length'])
    X_dummy = pd.get_dummies(X, columns=['algorithm', 'constraints'])
    y = pd.DataFrame(data_union, columns=['initial_pop_runtime'])

    data_union.to_csv(r'data_union_csp.csv')


def lcs_find_mean_sd(variant_num):
    fitness_threshold = False
    fitness_duration = 1
    fitness_lcs = 0
    constraints = 60
    lcs_results = pd.read_csv('run_lcs_07Jun.csv')

    data = lcs_results.loc[
        (lcs_results['variant_num'] == variant_num) & (lcs_results['fitness_threshold'] == fitness_threshold) & (
                lcs_results['fitness_duration'] == float(fitness_duration)) &
        (lcs_results['fitness_lcs'] == float(fitness_lcs)) &
        (lcs_results['success'] == 1) & (lcs_results['% constraints'] == int(constraints)) &
        (lcs_results['is_seq_valid'] == True)]

    print(data.shape)
    mean_p = (data['duration']).mean()
    sd_p = data['duration'].std()
    print("mean:", mean_p, "      sd, ", sd_p)


def anova_duration_lcs(variant_num):
    lcs_results = pd.read_csv('run_lcs_07Jun.csv')
    lcs_results = lcs_results.loc[
        (lcs_results['variant_num'] == variant_num) & (lcs_results['success'] == 1) & (
                lcs_results['is_seq_valid'] == True)]
    h1 = lcs_results.loc[
        (lcs_results['fitness_threshold'] == True) & (
                lcs_results['fitness_duration'] == 1) &
        (lcs_results['fitness_lcs'] == 0) & (lcs_results['% constraints'] == 100)]
    h2 = lcs_results.loc[
        (lcs_results['fitness_threshold'] == False) & (
                lcs_results['fitness_duration'] == 0.5) &
        (lcs_results['fitness_lcs'] == 0.5) & (lcs_results['% constraints'] == 100)]
    h3 = lcs_results.loc[
        (lcs_results['fitness_threshold'] == False) & (
                lcs_results['fitness_duration'] == 1) &
        (lcs_results['fitness_lcs'] == 0) & (lcs_results['% constraints'] == 100)]
    s1 = lcs_results.loc[
        (lcs_results['fitness_threshold'] == True) & (
                lcs_results['fitness_duration'] == 1) &
        (lcs_results['fitness_lcs'] == 0) & (lcs_results['% constraints'] == 60)]
    s2 = lcs_results.loc[
        (lcs_results['fitness_threshold'] == False) & (
                lcs_results['fitness_duration'] == 0.5) &
        (lcs_results['fitness_lcs'] == 0.5) & (lcs_results['% constraints'] == 60)]
    s3 = lcs_results.loc[
        (lcs_results['fitness_threshold'] == False) & (
                lcs_results['fitness_duration'] == 1) &
        (lcs_results['fitness_lcs'] == 0) & (lcs_results['% constraints'] == 60)]
    F, p = f_oneway(h1['duration'], h2['duration'], h3['duration'], s1['duration'], s2['duration'], s3['duration'])
    print("F: ", F, "P, ", p)
    frames = [h1, h2, h3, s1, s2, s3]
    results = pd.concat(frames)
    results = results['duration'].to_list()
    groups = [np.repeat('h1', repeats=h1.shape[0]), np.repeat('h2', repeats=h2.shape[0]),
              np.repeat('h3', repeats=h3.shape[0]), np.repeat('s1', repeats=s1.shape[0]),
              np.repeat('s2', repeats=s2.shape[0]), np.repeat('s3', repeats=s3.shape[0])]
    flat_groups = [item for sublist in groups for item in sublist]
    return results, flat_groups


if __name__ == "__main__":
    results, groups = anova_duration_lcs('ELE-3')
    tukey = pairwise_tukeyhsd(endog=results,
                              groups=groups,
                              alpha=0.05)
    print(tukey)

