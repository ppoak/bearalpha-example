import bearalpha as ba
from ..core import FactorBase


class FactorGrowth(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'growth'

class SalesGQ(FactorGrowth):
    def __init__(self):
        super().__init__('salesgq')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date, 1)[0]
        self.factor = ba.Stock.financial_indicator(report_date, report_date, 
            fields='fa_yoy_or').droplevel(0).fa_yoy_or

class ProfitGQ(FactorGrowth):
    def __init__(self):
        super().__init__('profitgq')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date, 1)[0]
        self.factor = ba.Stock.financial_indicator(report_date, report_date,
            fields='qfa_yoyprofit').droplevel(0).qfa_yoyprofit

class OcfGQ(FactorGrowth):
    def __init__(self):
        super().__init__('ocfgq')
    
    def calculate(self, date):
        report_dates = ba.nearest_report_period(date, 5)
        this_year = report_dates[-1]
        last_year = report_dates[0]
        ocf_thisyear = ba.Stock.cashflow_sheet(this_year, this_year,
            fields='net_cash_flows_oper_act').droplevel(0).net_cash_flows_oper_act
        ocf_lastyear = ba.Stock.cashflow_sheet(last_year, last_year,
            fields='net_cash_flows_oper_act').droplevel(0).net_cash_flows_oper_act
        self.factor = (ocf_thisyear - ocf_lastyear) / ocf_lastyear

class RoeGQ(FactorGrowth):
    def __init__(self):
        super().__init__('roegq')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date, 1)[0]
        self.factor = ba.Stock.financial_indicator(report_date, report_date,
            fields='fa_yoyroe').droplevel(0).fa_yoyroe


if __name__ == '__main__':
    factor = RoeGQ()
    value = factor('2020-01-06')
    print(value)
