# Copyright Builtvisible
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tensorflow as tf
import numpy as np
import pandas as pd
from causalimpact import CausalImpact
import csv
import sys
from datetime import datetime
import dtw
from sklearn import preprocessing
import logging
import time

def build(self, testset = pd.DataFrame(), dataset = pd.DataFrame(), metric = {'impressions':'sum'}, ranks = 'date',
            markets = 'page', begin_data = None, roll = 2, outlier = 1, test_cutoff = 0.85, data_cutoff = 0.85, verbose = False):
    """
    


    Builds a pd.DataFrame() by crossing two ranked -by dateime or else- unsorted and ungrouped datasets. 
    One concontains all data observations in the experiment, it can contain many observations at same rank. 
    The second one has a list of the test markets that underwent an experiment. 
    The column names must match between the list and the markets in global data (temporary until permanent solution).
    The resulting DataFrame is ready to be matched to its internal markets, see distance().
    ----
        testset: pd.DataFrame()
            The test set markets, testset.col.name must match dataset.col.name
        dataset: pd.DataFrame()
            The global raw data with test and all control markets, can be ungrouped and unsorted.
        metric: dict
            The column name for the target metric is the key and the aggregation method is the value, e.g. {'impressions':'sum'}
        col: str
            The column name for the markets shared by both dataframes, testset.col.name must match dataset.col.name case insensitive 
        begin_data: datetime str
            The start date for the dataset, creates a slice from this date forwards.
        ranks: str
            The column name that holds the ranking for the observations, defaults to 'date'.
            Accepts numerical and datetime ranking.
        roll: int
            The rolling window average. Used to smooth out data, defaults at 2
        outlier: int
            Eliminates outliers for observations that lie beyond this quantile, defaults to 1
        scaling: bool
            Applies scaling to the distances for easy interpretability, defaults to True
        min_test: int, must be less than min_data
            Minimum numbers of observations required from the test markets to be added to model. 
            I.e., in a dataset with 365 daily observations we would recommend (290-340)
        min_data: int
            Minimum numbers of observations required from the overall market dataset to be added to model.
            I.e., in a dataset with 365 daily observations we would recommend (325-360) 
        verbose: bool
            Wethear to save the remaining test and control markets in separate objects.
            
    Returns
    -------
        self: pd.DataFrame()
            Contains a sorted and grouped dataset with all data points for the test set aggregated by rank under 'TEST' market, see distance()
    Raises
    ------
        WIP
    """

    col = markets
    testset.columns = testset.columns.str.lower()
    dataset.columns = dataset.columns.str.lower()
    col = col.lower()

    assert testset[col].name == testset[col].name, 'Column names must match for the matched markets'

    if type(metric) == dict:
        metric_dict = metric
    else:
        raise ValueError('Metric must be a dictionary with the metric name as key and the aggregation method as the value, e.g. { "clicks" : "sum" }')

    causal_input = dataset.groupby([ranks, col]).agg(metric_dict).sort_values(ranks).reset_index()

    test_set = causal_input[causal_input[col].isin(testset[col])]
    causal_input = causal_input[~causal_input[col].isin(testset[col])]

    assert (test_set.iloc[1,:].all() != None)  & (test_set.iloc[0,:].all() != None), 'No markets match on test and data, check strings'

    if test_cutoff < 1 or data_cutoff < 1:
        causal_input = causal_input[~(causal_input[col].isin(testset[col]))]
        
        testcount = test_set.groupby([col]).count().sort_values(ranks, ascending=False).reset_index()
        fullcount = causal_input.groupby([col]).count().sort_values(ranks, ascending=False).reset_index()
        
        max_test = int( testcount[ranks].max() * test_cutoff )
        max_data = int( fullcount[ranks].max() * data_cutoff )
        
        for i in range(len(testcount)):
            if testcount.iloc[i][ranks] >= max_test:
                test_set_remainer = testcount.iloc[: i,]
                
        for i in range(len(fullcount)):
            if fullcount.iloc[i][ranks] >= max_data:
                causal_input_remainer = fullcount.iloc[: i,]

        test_set =  test_set[test_set[col].isin(test_set_remainer[col])]
        causal_set =  causal_input[causal_input[col].isin(causal_input_remainer[col])]
        causal_input = pd.concat([test_set, causal_set], ignore_index = True)
        causal_opt = causal_set.groupby([col]).count().sort_values(ranks, ascending=False).reset_index()
        test_opt = test_set.groupby([col]).count().sort_values(ranks, ascending=False).reset_index()


    if outlier < 1:
        test_set_clean = pd.DataFrame()
        for i in test_tops[col].unique():
            cutoff = test_set[test_set[col] == i].quantile(outlier)
            temp = test_set[test_set[col] == i]
            for key, value in metric_dict.items():
                temp = temp[temp[key] < cutoff.loc[key]]
                test_set_clean = pd.concat([test_set_clean, temp], ignore_index=True)
        test_set = test_set_clean
        causal_input = causal_input[~causal_input[col].isin(testcount[col])]
        causal_input = pd.concat([causal_input, test_set], ignore_index=True).sort_values(ranks).reset_index(drop=True)

    causal_input.loc[causal_input[col].isin(test_set[col]), col] = 'TEST'

    causal_input = causal_input.groupby([ranks, col]).agg(metric_dict).sort_values(ranks).reset_index()

    pvt_table = causal_input.pivot_table(index=ranks, columns=col, aggfunc=metric_dict).reset_index().fillna(0).set_index(ranks)

    if roll > 1:
        pvt_table = pvt_table.rolling(roll).mean()
        pvt_table = pvt_table[roll-1:]

    causal_control = pvt_table.melt(ignore_index=False).reset_index().sort_values(ranks).reset_index(drop=True).rename(columns = {None : "signal"})

    causal_control = causal_control.pivot_table(index=[ranks,col], columns='signal').reset_index(level=1).fillna(0)

    causal_control.columns = ["_".join(a) for a in causal_control.columns.to_flat_index()]

    if begin_data != None:
        causal_control = causal_control[causal_control.index >= begin_data]

    if verbose == True and (test_cutoff < 1 or data_cutoff < 1):
        return causal_control.reset_index(), test_opt, causal_opt

    return causal_control.reset_index()


def distance(self, causal_control, end_date,  col='page_', ranks='date',scaling=True):

    """
    


    Builds a pd.DataFrame() by finding all the dynamic time warped distances of each internal market against the 'TEST' set generated using build(). 
    ----
        causal_control: pd.DataFrame()
            The dataset built using build()
        end_date: datetime str
            The end date to match the markets, the intervention day.
        col: str
            The column name for the markets where 'TEST' is found.
        ranks: str
            The column name that holds the ranking for the observations, defaults to date.
            Accepts numerical and datetime ranking.
        scaling = bool
            Scaled distances max abs [1-0], defaults True.
            Examples: sum if impressions, sessions, etc. and mean if position, users, etc.
            
    Returns
    -------
        self: pd.DataFrame()
            Contains the time warped distances sorted from shortest to largest between test and global datasets.
    Raises
    ------
        WIP
    """

    
    causal_control = causal_control[causal_control[ranks] < end_date]
    
    total_time = 0
    final = {}
    for j in causal_control.columns[~causal_control.columns.isin([col, ranks])]:
        t_start_0 = time.time()
        print(f"Starting distances for {j}")
        print('')
        distances = {}
        temp = causal_control[[col, j]]
        for i in temp[col].unique():
            distances[i] = dtw.dtw(causal_control[causal_control[col] == 'TEST'][j], causal_control[causal_control[col] == i][j],open_end=True).distance
        final[j] = pd.DataFrame.from_dict(distances, orient='index', columns=['dist']).sort_values('dist', ascending=True)[1:].reset_index()
        time_taken = time.time() - t_start_0
        total_time += time_taken
        print(f"Metric {j} completed. Time taken: {time_taken / 60:0.2f} minutes")
        print('')
    

    if scaling == True:
        for key, value in final.items():
            x = value.dist[:].values
            min_max_scaler = preprocessing.MaxAbsScaler()
            x_scaled = min_max_scaler.fit_transform(x.reshape(-1, 1))
            final[key] = final[key].rename({'index':col}, axis=1)   
            final[key].dist = x_scaled    
    
    if total_time > 3600:
        print(f"All metrics complete. Total time: {total_time // 60:0.2f} h {total_time / 60:0.2f} mins")
    else:
        print(f"All metrics complete. Total time: {total_time / 60:0.2f} mins")
    
    return  final


def fit(int_time, end, distances,
        causal_data, alpha = 0.95, events_per_season = 1, 
        seasons = 1, btest = 0, standardize = False):

    """
    


    Fits a causal impact model to the build() dataset using the controls defined by distance(), it is recommended to constrain the total markets in distance() to less than 100.
    ----
        int_time:
            The intervention date, start of test period
        end:
            The end date for the test
        distances:
            The dataset with the distances generated by distance(), recommended to cap it at .iloc[0:100]
        causal_data: pd.DataFrame()
            The dataset built using build()
        col: str
            The column name for the markets where 'TEST' is found.
        ranks: str
            The column name that holds the ranking for the observations, defaults to date.
            Accepts numerical and datetime ranking.
        scaling = bool
            Scaled distances max abs [1-0], defaults True.
            Examples: sum if impressions, sessions, etc. and mean if position, users, etc.
            
    Returns
    -------
        self: pd.DataFrame()
            Contains the time warped distances sorted from shortest to largest between test and global datasets.
    Raises
    ------
        WIP
    """

    distances = distances.append({'page':'TEST'}, ignore_index=True)

    pvt_longer = causal_data.merge(distances['page'], how='inner', on=['page']).sort_values('date').reset_index(drop=True)
    
    raw_ts = pvt_longer.pivot_table(index='date', columns='page', values='value').reset_index()

    partition1 = raw_ts[raw_ts.date == int_time].index.values[0].item()

    partition2 = raw_ts[raw_ts.date == end].index.values[0].item()
    
    pre_period = [0,  partition1 - 1]
    
    post_period = [partition1, partition2]

    final = raw_ts.sort_values('date').reset_index(drop=True)
    
    final = final.drop(['date'], axis=1)

    print('Calculating Causal Impact....')
    print('')
    print('')
    
    ci = CausalImpact(final, pre_period, post_period, alpha=alpha, model_args = {'nseasons': events_per_season,'season_duration': seasons})

    print(ci.summary())
    print(ci.plot())
    
    bt_pre_period = [0,  partition1 - 1 -btest]
    bt_post_period = [partition1 -btest, partition1 -1]
    
    if btest != 0:
        print('')
        print('')
        print('Calculating Backtest...')
        print('')
        print('')
        cibt = CausalImpact(final, bt_pre_period, bt_post_period, alpha=alpha, model_args = {'nseasons': events_per_season,'season_duration': seasons})
    
        print(cibt.summary())
        print(cibt.plot())
        
        return ci, cibt

    return ci
