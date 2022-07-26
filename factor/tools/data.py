import bearalpha as ba


@ba.Cache(prefix='factor_data', expire_time=259200)
def factor_data(factor, start: str, end: str, freq = ba.CBD):
    dates = ba.date_range(start=start, end=end, freq=freq)
    data = []
    for date in ba.Track(dates):
        data.append(factor(date))
    data = ba.concat(data)
    return data.iloc[:, 0]

@ba.Cache(prefix='group_mapping', expire_time=259200)
def group_mapping(start: str, end: str, freq = ba.CBD, source: str = 'citics'):
    stock = ba.Stock(ba.Cache().get('local'))
    dates = ba.date_range(start=start, end=end, freq=freq)
    data = []
    for date in ba.Track(dates):
        data.append(stock.plate_info(start=date, end=date, 
            fields='first_industry_name', and_=f'source = "{source}"'))
    data = ba.concat(data)
    return data
    
@ba.Cache(prefix='market_value', expire_time=259200)
def market_value(start: str, end: str, freq = ba.CBD):
    stock = ba.Stock(ba.Cache().get('local'))
    dates = ba.date_range(start=start, end=end, freq=freq)
    data = []
    for date in ba.Track(dates):
        data.append(stock.derivative_indicator(start=date, end=date, fields='market_cap_2'))
    data = ba.concat(data)
    return data