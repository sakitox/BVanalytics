class SEOCausal(CausalImpact):
    def __init__(self):
        super(CausalImpact, self).__init__()
    
    def fit(self, int_time, start, end, 
            test_set, dataset, alpha, 
            events, seasons, btest, 
            standardize):
        
        
        
        
        
        
        
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
        

            testset.columns = testset.columns.str.lower()
            dataset.columns = dataset.columns.str.lower()
            col = col.lower()
            
            assert testset[col].name == testset[col].name, 'Column names must match for the matched markets'
            
            causal_input = dataset
            
            test_set = causal_input[causal_input[col].isin(pdp[col])]
            
            test_set_clean = pd.DataFrame()
            
            for i in test_set[col]:
                cutoff = test_set[test_set[col] == i].quantile(outlier)
                temp = test_set[test_set[col] == i]
                temp = temp[temp[metric] < cutoff[0]]
                test_set_clean = pd.concat([test_set_clean, temp], ignore_index=True)
                test = causal_input[causal_input[col].isin(testset[col])]
            
            test = test_set_clean
            causal_input = causal_input[~causal_input.page.isin(testcount.page)]
            causal_input = pd.concat([causal_input, test_set_clean], ignore_index=True).sort_values(ranks)
            
            assert (test.iloc[1,:].all() != None)  & (test.iloc[0,:].all() != None), 'No markets match on test and data, check strings'

            testcount = test.groupby([col]).count().sort_values(metric, ascending=False).reset_index()

            assert testcount[ranks] > min_test, 'min_test must be lower than the maximum number of observations in testset'
            
            test_tops = testcount[testcount[danks] > min_test].reset_index()

            causal_input.loc[causal_input[col].isin(test_tops[col]), col] = 'TEST'
            
            if metric2 == 'sum':
                causal_input = causal_input.groupby([ranks, col]).sum().sort_values(metric, ascending=False).reset_index()
            elif metric2 == 'mean':
                causal_input = causal_input.groupby([ranks, col]).mean().sort_values(metric, ascending=False).reset_index()
            else:
                raise ValueError('Supported aggregators are sum and mean')
            
            marketcount = causal_input.groupby([col]).count().sort_values(metric, ascending=False).reset_index()
            
            control_urls = marketcount[marketcount[ranks] > min_data].reset_index()
            
            assert marketcount[ranks] > min_data, 'min_data must be lower than the maximum number of observations in dataset'
            
            causal_control = causal_input.loc[causal_input[col].isin(control_urls[col]),]

            pvt_table = causal_control.pivot_table(index=ranks, columns=col, values=metric, aggfunc=metric2).reset_index().fillna(0).set_index(ranks)

            pvt_table = pvt_table.rolling(roll).mean()

            pvt_table = pvt_table[roll-1:]

            causal_control = pvt_table.melt(ignore_index=False).reset_index().sort_values(ranks).reset_index(drop=True)

            markets = {}
            for i in causal_control[[col]][col].unique():
                markets[i] = causal_control[causal_control[col] == i].sort_values(ranks).reset_index(drop=True)[['value']]

            distances = {}
            for i in causal_control[[col]][col].unique():
                distances[i] = dtw.dtw(markets['TEST'], markets[i]).distance
                
            final = pd.DataFrame.from_dict(distances, orient='index', columns=['dist']).sort_values('dist')[1:].reset_index()

            if scaling == True:
                x = final.dist[:].values
                min_max_scaler = preprocessing.StandardScaler()
                x_scaled = min_max_scaler.fit_transform(x.reshape(-1, 1))
                final = pd.DataFrame(x_scaled)
            
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