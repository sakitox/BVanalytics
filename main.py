class SEOCausal(CausalImpact):
    def __init__(self):
        super(CausalImpact, self).__init__()
    
    def build(self, testset=pd.DataFrame(), dataset=pd.DataFrame(), metric='impressions', ranks='date',
                col='page', begin_data = None, roll=2, outlier=1, min_test=1, min_data=1, metric2='sum'):

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
            metric: str, dict
                The column name for the target variable. Accepts multi-variable input as a dictionary with key = column name and the value is the aggregation method (mean, sum, etc.)
            col: str
                The column name for the markets, testset.col.name must match dataset.col.name case independent 
            begin_data: datetime str
                The start date for the dataset to be built
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
                Function by which to aggregate the data. Not used if metric input is a dictionary.
                Examples: sum if impressions, sessions, etc. and mean if position, users, etc.
                
        Returns
        -------
            self: pd.DataFrame()
                Contains a sorted and grouped dataset with all data points for the test set aggregated by rank under 'TEST' market, see distance()
        Raises
        ------
            WIP
        """

        testset.columns = testset.columns.str.lower()
        dataset.columns = dataset.columns.str.lower()
        col = col.lower()
        
        assert testset[col].name == testset[col].name, 'Column names must match for the matched markets'
        
        if type(metric) == str:
            metric_dict = {metric : metric2}
        elif type(metric) == dict:
            metric_dict = metric
        else:
            raise ValueError('Metric must be a string or a dictionary')

        
        causal_input = dataset.groupby([ranks, col]).agg(metric_dict).sort_values(ranks).reset_index()

        test_set = causal_input[causal_input[col].isin(testset[col])]
        
        assert (test_set.iloc[1,:].all() != None)  & (test_set.iloc[0,:].all() != None), 'No markets match on test and data, check strings'

        testcount = test_set.groupby([col]).count().sort_values(ranks, ascending=False).reset_index()
        
        assert testcount[ranks].max() >= min_test, 'min_test must be lower than the maximum number of observations in testset'
        
        test_tops = testcount[testcount[ranks] >= min_test].reset_index() #to be expanded, same with row 106
        
        test_set =  causal_input[causal_input[col].isin(test_tops[col])]
        test_set = test_set.groupby([ranks, col]).agg(metric_dict).sort_values(ranks).reset_index()
            
        test_set_clean = pd.DataFrame()
        
        if outlier < 1:
            for i in test_tops[col].unique():
                cutoff = test_set[test_set[col] == i].quantile(outlier)
                temp = test_set[test_set[col] == i]
                for key, value in metric_dict.items():
                    temp = temp[temp[key] < cutoff.loc[key]]
                    test_set_clean = pd.concat([test_set_clean, temp], ignore_index=True)
            test_set = test_set_clean
            causal_input = causal_input[~causal_input[col].isin(testcount[col])]
            causal_input = pd.concat([causal_input, test_set], ignore_index=True).sort_values(ranks).reset_index(drop=True)
        
        test_items = causal_input[causal_input[col].isin(test_tops[col])]
        
        causal_input.loc[causal_input[col].isin(test_tops[col]), col] = 'TEST'
        
        causal_input = causal_input.groupby([ranks, col]).agg(metric_dict).sort_values(ranks).reset_index()
        
        marketcount = causal_input.groupby([col]).count().sort_values(ranks, ascending=False).reset_index()

        if marketcount[marketcount[col] == 'TEST'][ranks].max() <= min_data:
            min_data = marketcount[marketcount[col] == 'TEST'][ranks].max()
        
        assert marketcount[ranks].max() >= min_data, 'min_data must be lower than the maximum number of observations in dataset'    
        assert min_test <= min_data, 'Test observations have to be equal or higher than cutoff point'
        
        control_urls = marketcount[marketcount[ranks] >= min_data].reset_index() #to be expanded, same with row 75

        causal_control = causal_input.loc[causal_input[col].isin(control_urls[col]),]

        pvt_table = causal_control.pivot_table(index=ranks, columns=col, aggfunc=metric_dict).reset_index().fillna(0).set_index(ranks)

        if roll > 1:
            pvt_table = pvt_table.rolling(roll).mean()
            pvt_table = pvt_table[roll-1:]

        causal_control = pvt_table.melt(ignore_index=False).reset_index().sort_values(ranks).reset_index(drop=True).rename(columns = {None : "signal"})

        causal_control = causal_control.pivot_table(index=[ranks,col], columns='signal').reset_index(level=1).fillna(0)

        causal_control.columns = ["_".join(a) for a in causal_control.columns.to_flat_index()]

        if begin_data != None:
            causal_control = causal_control[causal_control[ranks] >= begin_data]
        
        return causal_control

    
    def distance(self, causal_control, end_date,  col='page', ranks='date',scaling=True):

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
        
        markets = {}
        for i in causal_control[col].unique():
            markets[i] = causal_control[causal_control[col] == i].sort_values(ranks).reset_index(drop=True)[['value']]
        
        distances = {}
        for i in causal_control[col].unique():
            distances[i] = dtw.dtw(markets['TEST'], markets[i],open_end=True).distance
            
        final = pd.DataFrame.from_dict(distances, orient='index', columns=['dist']).sort_values('dist', ascending=True)[1:].reset_index()

        if scaling == True:
            x = final.dist[:].values
            min_max_scaler = preprocessing.MaxAbsScaler()
            x_scaled = min_max_scaler.fit_transform(x.reshape(-1, 1))
            final.dist = x_scaled
        
        final = final.rename({'index':col}, axis=1)
        
        return  final
    
    
    def fit(int_time, end, distances,agg,
            build, alpha = 0.95, events_per_season = 1, 
            seasons = 1, btest = 0, standardize = False):

        """
        Fits a causal impact model to the build() dataset using the controls defined by distance(), it is recommended to constrain the total markets in distance() to less than 100.
        ----
            causal_control: pd.DataFrame()
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

        pvt_longer = causal_input.merge(distances['page'], how='inner', on=['page']).sort_values('date').reset_index(drop=True)
        
        raw_ts = pvt_longer.pivot_table(index='date', columns='page', values='value', aggfunc=agg).reset_index()

        partition1 = raw_ts[raw_ts.date == int_time].index.values[0].item()

        partition2 = raw_ts[raw_ts.date == end].index.values[0].item()
        
        pre_period = [0,  partition1 - 1]
        
        post_period = [partition1, partition2]

        final = raw_ts.sort_values('date').reset_index(drop=True)
        
        final = final.drop(['date'], axis=1)

        print('Calculating Causal Impact....')
        
        ci = CausalImpact(final, pre_period, post_period, alpha=alpha, model_args = {'nseasons': events_per_season,'season_duration': seasons})

        print(ci.summary())
        print(ci.plot())
        
        bt_pre_period = [0,  partition1 - 1 - btest]
        bt_post_period = [partition1 - btest, partition1 -1]
        
        if btest != 0:
            print('')
            print('')
            print('')
            print('Calculating Backtest...')
            cibt = CausalImpact(final, bt_pre_period, bt_post_period, alpha=alpha, model_args = {'nseasons': events_per_season,'season_duration': seasons})
        
            print(cibt.summary())
            print(cibt.plot())
            
            return ci, cibt

        return ci
        
        
    def Rtransform(self, testset, dataset, metric,  #To do
                  roll, nmarkets, min_test, min_data):
        return
    
    def fit_transform(self, int_time, start, end,  #To do,
                    test_set, dataset, alpha, 
                    events, seasons, btest, 
                    standardize, testset, dataset, metric,
                    roll, min_test, min_data)
        return