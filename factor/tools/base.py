import pandas as pd
import bearalpha as ba
from functools import wraps


class FactorBase:
    '''Base Class for all factors to be defined
    ============================================

    There are five steps to define a factor:

        1. Define the class inheriting FactorBase
        
        2. rewrite `basic_info` according to your needs, this
            method provides basic information like stocks
            in stock pool and corresponding industry
        
        3. rewrite `calcuate_factor` according to your needs,
            this method can provide the factor value in a series form
            
        4. rewrite `factor_process` according to your needs,
            the process inculdes standardization, deextreme, missing fill

        5. rewrite `factor_modify` according to your needs,
            this method adjusted the index into multiindex form and rename
    '''
    def __init__(self, name):
        self.name = name
        self.datasource = ba.Stock(ba.Cache().get('local'))

    def info(self, date):
        self.stocks = self.datasource.index_weights(date, date, 
            code='000001.XSHG').index.levels[1].to_list()

    def calculate(self, date):
        raise NotImplementedError

    def process(self, date):
        grouper = self.datasource.plate_info(date, date, 
            fields='first_industry_name', and_='source="citics"').droplevel(0)
        self.factor = self.factor.preprocessor.deextreme(method='mad', grouper=grouper)\
            .preprocessor.fillna(method='mean', grouper=grouper)\
            .preprocessor.standarize(method='zscore', grouper=grouper)
        self.factor = self.factor.loc[self.factor.index.intersection(self.stocks)]
    
    def modify(self, date):
        self.factor.index = pd.MultiIndex.from_product([[ba.str2time(date)], self.factor.index])
        self.factor.index.names = ["date", "asset"]
        self.factor.columns = [self.name]

    def __call__(self, date) -> ...:
        self.info(date)
        self.calculate(date)
        self.process(date)
        self.modify(date)
        return self.factor
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name


class Factor:
    def __init__(self, name: str,
                 pool: 'list | pd.Index | pd.MultiIndex' = None,
                 deextreme: str = 'mad',
                 standardize: str = 'zscore',
                 fillna: str = 'mean',
                 grouper = None,
                 *args, **kwargs):
        self.name = name
        self.pool = pool
        self.deextreme = deextreme
        self.standardize = standardize
        self.fillna = fillna
        self.grouper = grouper
        self.args = args
        self.kwargs = kwargs

    def filter_pool(self) -> 'pd.Series | pd.DataFrame':
        if self.pool is None:
            return self.factor
        
        elif isinstance(self.pool, str):
            stocks = ba.Api.index_weight(start = self.factor.index.levels[0][0], 
                end=self.factor.index.levels[0][1], 
                conditions=f'c_indexCode={self.pool}')
            stocks = stocks.index.intersection(self.factor.index)
            return self.factor.loc[stocks.index]

        elif isinstance(self.pool, pd.MultiIndex):
            stocks = self.pool.index.intersection(self.factor.index)
            return self.factor.loc[stocks]

        elif isinstance(self.pool, pd.Index):
            stocks = self.pool.index.intersection(self.factor.index.levels[1])
            return self.factor.loc[stocks]
        
        elif isinstance(self.pool, list):
            stocks = pd.Index(stocks)
            stocks = stocks.index.intersection(self.factor.index.levels[1])
            return self.factor.loc[stocks]
    
    def preprocess(self):
        factor = self.factor.preprocessor.deextreme(self.deextreme, self.grouper)
        factor = factor.preprocessor.standarize(self.standardize, self.grouper)
        factor = factor.preprocessor.fillna(self.fillna, self.grouper)
        return factor
    
    def postprocess(self):
        if isinstance(self.factor, pd.DataFrame) and isinstance(self.factor.index, pd.MultiIndex):
            if self.factor.columns.size != 1:
                raise ValueError('factor must be a single columned dataframe')
            factor = self.factor.iloc[:, 0]
        
        elif isinstance(self.factor, pd.DataFrame) and isinstance(self.factor.index, pd.DatetimeIndex):
            factor = self.factor.stack()
        
        elif isinstance(self.factor, pd.Series):
            factor = self.factor

        factor.index.names = ['datetime', 'asset']
        factor.name = self.name
        return factor
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.factor = func(*args, **kwargs)
            self.factor = self.preprocess()
            self.factor = self.filter_pool()
            self.factor = self.postprocess()
            return self.factor
        return wrapper

