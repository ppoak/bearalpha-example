import bearalpha as ba
from ..core import FactorBase

class FactorLeverage(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'leverage'

class FinancialLeverage(FactorLeverage):
    def __init__(self):
        super().__init__('financialleverage')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date)[0]
        asset = ba.Stock.balance_sheet(report_date, report_date, 
            fields='tot_assets').droplevel(0).tot_assets
        liab = ba.Stock.balance_sheet(report_date, report_date,
            fields='tot_liab').droplevel(0).tot_liab
        self.factor = asset / (asset - liab)
    
class DebtEquityRatio(FactorLeverage):
    def __init__(self):
        super().__init__('debtequityratio')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date)[0]
        asset = ba.Stock.balance_sheet(report_date, report_date, 
            fields='tot_assets').droplevel(0).tot_assets
        liab = ba.Stock.balance_sheet(report_date, report_date,
            fields='tot_liab').droplevel(0).tot_liab
        noncurliab = ba.Stock.balance_sheet(report_date, report_date,
            fields='tot_non_cur_liab').droplevel(0).tot_non_cur_liab
        self.factor = noncurliab / (asset - liab)
    
class CashRatio(FactorLeverage):
    def __init__(self):
        super().__init__('cashratio')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date)[0]
        cash = ba.Stock.balance_sheet(report_date, report_date,
            fields='monetary_cap').droplevel(0).monetary_cap
        asset = ba.Stock.balance_sheet(report_date, report_date, 
            fields='tot_assets').droplevel(0).tot_assets
        self.factor = cash / asset

class CurrentRatio(FactorLeverage):
    def __init__(self):
        super().__init__('currentratio')
    
    def calculate(self, date):
        report_date = ba.nearest_report_period(date)[0]
        self.factor = ba.Stock.financial_indicator(report_date, report_date,
            fields='fa_current').droplevel(0).fa_current

if __name__ == "__main__":
    factor = CurrentRatio()
    print(factor('20200106'))