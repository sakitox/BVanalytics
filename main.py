class SEOCausal(CausalImpact):
    def __init__(self):
        super(CausalImpact, self).__init__()
    
    def fit(self, int_time, start, end, 
            test_set, dataset, alpha, 
            events, seasons, btest, 
            standardize):
        
        
        
        
        
        
        
        return 
    
    def distance(testset=pd.DataFrame(), dataset=pd.DataFrame(), metric='str',
                col='page', roll=2, outlier = 0.98, min_test, min_data, metric2='sum'):

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
            roll: int
                The rolling window average. Used to smooth out data and, defaults at 2
            outlier: int
                Eliminates outliers for observations that lie beyond this value, defaults at 0.98
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
        
        causal_input = dataset

        test = causal_input[causal_input[col].isin(testset[col])]

        testcount = test.groupby([col]).count().sort_values(metric, ascending=False).reset_index()

        test_tops = testcount[testcount['date'] > min_test].reset_index()

        causal_input.loc[causal_input[col].isin(test_tops[col]), col] = 'TEST'
        
        causal_input = causal_input.groupby(['date', col]).sum().sort_values(metric, ascending=False).reset_index()
        
        marketcount = causal_input.groupby([col]).count().sort_values(metric, ascending=False).reset_index()
        
        control_urls = marketcount[marketcount['date'] > min_data].reset_index() 
        
        causal_control = causal_input.loc[causal_input[col].isin(control_urls[col]),]

        pvt_table = causal_control.pivot_table(index='date', columns=col, values=metric, aggfunc=metric2).reset_index().fillna(0).set_index('date')

        pvt_table = pvt_table.rolling(roll).mean()

        pvt_table = pvt_table[roll-1:]

        causal_control = pvt_table.melt(ignore_index=False).reset_index().sort_values('date').reset_index(drop=True)

        markets = {}
        for i in causal_control[[col]][col].unique():
            markets[i] = causal_control[causal_control[col] == i].sort_values('date').reset_index(drop=True)[['value']]

        distances = {}
        for i in causal_control[[col]][col].unique():
            distances[i] = dtw.dtw(markets['TEST'], markets[i]).distance
            
        final = pd.DataFrame.from_dict(distances, orient='index', columns=['dist']).sort_values('dist')[1:].reset_index()

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