import bearalpha as ba


@ba.Cache(prefix='backtest_market_daily', expire_time=18000)
def market_daily(
    code: 'str | list', 
    start: str = None, 
    end: str = None, 
) -> ba.DataFrame:
    codes = ba.item2list(code)
    datas = []
    for c in codes:
        data = ba.AkShare.market_daily(code=c, start=start, end=end)
        data = data.rename(columns={'复权开盘': 'open', '复权收盘': 'close', '复权最高': 'high',
            '复权最低': 'low', '成交量': 'volume'}).loc[:, ['open', 'close', 'high', 'low', 'volume']]
        data.index = ba.MultiIndex.from_product([data.index, [c]], names=['datetime', 'asset'])
        datas.append(data)
    datas = ba.concat(datas, axis=0).sort_index()
    return datas


@ba.Cache(prefix='backtest_etf_market_daily', expire_time=18000)
def etf_market_daily(code: 'str | list', start: str = None, end: str = None):
    codes = ba.item2list(code)
    datas = []
    for c in codes:
        data = ba.AkShare.etf_market_daily(code, start, end)['累计净值']
        data = data.rename(columns={'净值日期': 'datetime', '累计净值': 'close'})
        data = data.set_index('datetime')
        data.index = ba.MultiIndex.from_product([data.index, [c]], names=['datetime', 'asset'])
        datas.append(data)
    datas = ba.concat(datas, axis=0).sort_index()
    return datas


if __name__ == '__main__':
    print(market_daily('000001.SZ', '2019-01-01', '2019-01-31'))