class SEOCausal(CausalImpact):
    def __init__(self):
        super(CausalImpact, self).__init__()
    
    def fit(int_time, start, end, distances, 
            causal_input, alpha = 0.95, events_per_season = 1, 
            seasons = 1, btest = 0, standardize = False):
        
        distances = distances.append({'index':'TEST'}, ignore_index=True)
        
        pvt_longer = causal_input.merge(distances['index'], how='inner', on=['page']).drop_duplicates().sort_values('date').reset_index(drop=True)
        
        raw_ts = pvt_longer.pivot_table(index='date', columns='page', values='value', aggfunc='sum').reset_index()
        
        partition1 = raw_ts[raw_ts.date == '2021-11-12'].index.values.astype(int)[0]
        
        partition2 = raw_ts[raw_ts.date == '2021-11-24'].index.values.astype(int)[0]
        
        pre_period = [0,  partition1 - 1]
        
        post_period = [partition1, 324]
        
        final = raw_ts.[['value','page']]
        
        ci = CausalImpact(final, pre_period, post_period, alpha=0.05, model_args = {'nseasons': 14,'season_duration': 2})

        print(ci.summary())

        ci.plot()
        
        return 
    
    def distance(testset=pd.DataFrame(), dataset=pd.DataFrame(), metric='str',
                col='page', roll=2, outlier = 0.98, scaling=True, min_test, min_data, metric2='sum'):

        """
        Builds a pd.DataFrame() object with the markets in dataset and their dtw distances in relation to testset
        ----
            testset: pd.DataFrame()
                The test set markets, testset.col.name must match dataset.col.name
            dataset: pd.DataFrame()
                The global raw data with test and all control markets, can be ungrouped and unsorted.
            metric: str
                The column name for the target variable
            col: str
                The column name for the markets, testset.col.name must match dataset.col.name case independent 
            ranks: str
                The column name that holds the ranking for the observations, defaults to date.
                Accepts numerical and datetime ranking
            roll: int
                The rolling window average. Used to smooth out data and, defaults at 2
            outlier: int
                Eliminates outliers for observations that lie beyond this value, defaults at 0.98
            scaling: bool
                Applies scaling to the distances for easy interpretability, defaults to True
            min_test: int, must be less than min_data
                Minimum numbers of observations required from the test markets to be added to model. 
                I.e., in a dataset with 20 markets and 365 daily observations we would recommend (290-340)
            min_data: int
                Minimum numbers of observations required from the overall market dataset to be added to model.
                I.e., in a dataset with 20 markets and 365 daily observations we would recommend (325-360) 
            metric2 = str
                Function by which to aggregate the data.
                Examples: sum if impressions, sessions, etc. and mean if position, users, etc.
                
        Returns
        -------
            self: pd.DataFrame()
                Contains the time warped distances sorted from shortest to largest between test and global datasets.
        Raises
        ------
            WIP
        """
        
    def causal_input(testset=pd.DataFrame(), dataset=pd.DataFrame(), metric='impressions', ranks='date',
                col='page', roll=2, outlier=1, scaling=True, min_test=1, min_data=1, metric2='sum'):

        testset.columns = testset.columns.str.lower()
        dataset.columns = dataset.columns.str.lower()
        col = col.lower()
        
        assert testset[col].name == testset[col].name, 'Column names must match for the matched markets'
        
        if metric2 == 'sum':
            causal_input = dataset.groupby([ranks, col]).sum().sort_values(ranks, ascending=False).reset_index()
        elif metric2 == 'mean':
            causal_input = causal_input.groupby([ranks, col]).mean().sort_values(ranks, ascending=False).reset_index()
        else:
            raise ValueError('Supported aggregators are sum and mean')

        test_set = causal_input[causal_input[col].isin(pdp[col])]
        
        assert (test_set.iloc[1,:].all() != None)  & (test_set.iloc[0,:].all() != None), 'No markets match on test and data, check strings'

        testcount = test_set.groupby([col]).count().sort_values(metric, ascending=False).reset_index()
        
        assert testcount[metric].max() >= min_test, 'min_test must be lower than the maximum number of observations in testset'
        
        test_tops = testcount[testcount[ranks] >= min_test].reset_index()
        
        if metric2 == 'sum':
            test_set =  causal_input[causal_input[col].isin(test_tops[col])]
            test_set = test_set.groupby([ranks, col]).sum().sort_values(ranks, ascending=False).reset_index()
        elif metric2 == 'mean':
            test_set =  causal_input[causal_input[col].isin(test_tops[col])]
            test_set = test_set.groupby([ranks, col]).mean().sort_values(ranks, ascending=False).reset_index()
            
        if outlier != 1:
            test_set_clean = pd.DataFrame()
            for i in test_tops[col].unique():
                cutoff = test_set[test_set[col] == i].quantile(outlier)
                temp = test_set[test_set[col] == i]
                temp = temp[temp[metric] < cutoff[0]]
                test_set_clean = pd.concat([test_set_clean, temp], ignore_index=True)
                test_set = test_set_clean

            causal_input = causal_input[~causal_input[col].isin(testcount[col])]
            causal_input = pd.concat([causal_input, test_set], ignore_index=True).sort_values(ranks)
        
        causal_input.loc[causal_input[col].isin(test_tops[col]), col] = 'TEST'
        
        if metric2 == 'sum':
            causal_input = causal_input.groupby([ranks, col]).sum().sort_values(ranks, ascending=True).reset_index()
        elif metric2 == 'mean':
            causal_input = causal_input.groupby([ranks, col]).mean().sort_values(ranks, ascending=True).reset_index()
        else:
            raise ValueError('Supported aggregators are sum and mean')
        
        marketcount = causal_input.groupby([col]).count().sort_values(metric, ascending=False).reset_index()

        if marketcount[marketcount[col] == 'TEST'][metric].max() <= min_data:
            min_data = marketcount[marketcount[col] == 'TEST'][metric].max()
        
        assert marketcount[metric].max() >= min_data, 'min_data must be lower than the maximum number of observations in dataset'    
        assert min_test >= min_data, 'Test observations have to be equal or higher than cutoff point'
        
        control_urls = marketcount[marketcount[ranks] >= min_data].reset_index()

        causal_control = causal_input.loc[causal_input[col].isin(control_urls[col]),]

        pvt_table = causal_control.pivot_table(index=ranks, columns=col, values=metric, aggfunc=metric2).reset_index().fillna(0).set_index(ranks)

        pvt_table = pvt_table.rolling(roll).mean()

        pvt_table = pvt_table[roll-1:]

        causal_control = pvt_table.melt(ignore_index=False).reset_index().sort_values(ranks).reset_index(drop=True)
        
        return causal_control

    def distance(causal_control, col='page', ranks='date',scaling=True):
        
        markets = {}
        for i in causal_control[col].unique():
            markets[i] = causal_control[causal_control[col] == i].sort_values(ranks).reset_index(drop=True)[['value']]
        
        distances = {}
        for i in causal_control[col].unique():
            distances[i] = dtw.dtw(markets['TEST'], markets[i]).distance
            
        final = pd.DataFrame.from_dict(distances, orient='index', columns=['dist']).sort_values('dist', ascending=True)[1:].reset_index()

        if scaling == True:
            x = final.dist[:].values
            min_max_scaler = preprocessing.MaxAbsScaler()
            x_scaled = min_max_scaler.fit_transform(x.reshape(-1, 1))
            final.dist = x_scaled
        
        return  final
        
    def Rtransform(self, testset, dataset, metric,  #To do
                  roll, nmarkets, min_test, min_data):
        return
    
    def fit_transform(self, int_time, start, end,  #To do,
                    test_set, dataset, alpha, 
                    events, seasons, btest, 
                    standardize, testset, dataset, metric,
                    roll, min_test, min_data)
        return