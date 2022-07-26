import bearalpha as ba
from ..core import FactorBase

class FactorQuanlity(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.kalss = 'quanlity'

class RoeQ(FactorQuanlity):
    def __init__(self):
        super().__init__('roeq')
    
    def calculate(self, date):
        report_period = ba.nearest_report_period(date)[0]
        self.factor = ba.Stock.financial_indicator(report_period, report_period,
            fields='qfa_roe').droplevel(0).qfa_roe

class RoeTTM(FactorQuanlity):
    def __init__(self):
        super().__init__('roettm')
    
    def calculate(self, date):
        self.factor = ba.Stock.pit_financial(date, date,
            fields='s_dfa_roe_ttm').droplevel(0).s_dfa_roe_ttm

class RoaQ(FactorQuanlity):
    def __init__(self):
        super().__init__('roaq')
    
    def calculate(self, date):
        report_period = ba.nearest_report_period(date)[0]
        self.factor = ba.Stock.financial_indicator(report_period, report_period,
            fields='fa_roa2').droplevel(0).fa_roa2

class RoaTTM(FactorQuanlity):
    def __init__(self):
        super().__init__('roattm')
    
    def calculate(self, date):
        self.factor = ba.Stock.pit_financial(date, date,
            fields='s_dfa_roa2_ttm').droplevel(0).s_dfa_roa2_ttm

class GrossProfitMarginQ(FactorQuanlity):
    def __init__(self):
        super().__init__('grossprofitmarginq')
    
    def calculate(self, date):
        report_period = ba.nearest_report_period(date)[0]
        self.factor = ba.Stock.financial_indicator(report_period, report_period,
            fields='fa_grossmargin').droplevel(0).fa_grossmargin

class GrossProfitMarginTTM(FactorQuanlity):
    def __init__(self):
        super().__init__('grossprofitmarginttm')
    
    def calculate(self, date):
        self.factor = ba.Stock.pit_financial(date, date,
            fields='s_dfa_grossmargin_ttm').droplevel(0).s_dfa_grossmargin_ttm

class ProfitMarginQ(FactorQuanlity):
    def __init__(self):
        super().__init__('profitmarginq')
    
    def calculate(self, date):
        report_period = ba.nearest_report_period(date)[0]
        self.factor = ba.Stock.financial_indicator(report_period, report_period,
            fields='fa_deductedprofit').droplevel(0).fa_deductedprofit

class ProfitMarginTTM(FactorQuanlity):
    def __init__(self):
        super().__init__('profitmarginttm')
    
    def calculate(self, date):
        self.factor = ba.Stock.pit_financial(date, date,
            fields='s_dfa_deductedprofit_ttm').droplevel(0).s_dfa_deductedprofit_ttm

class AssetTurnoverQ(FactorQuanlity):
    def __init__(self):
        super().__init__('assetturnoverq')

    def calculate(self, date):
        report_period = ba.nearest_report_period(date)[0]
        self.factor = ba.Stock.financial_indicator(report_period, report_period,
            fields='fa_assetsturn').droplevel(0).fa_assetsturn

class AssetTurnoverTTM(FactorQuanlity):
    def __init__(self):
        super().__init__('assetturnoverttm')
    
    def calculate(self, date):
        self.factor = ba.Stock.pit_financial(date, date,
            fields='s_dfa_currtassetstrate').droplevel(0).s_dfa_currtassetstrate

class OperationCashflowRatioQ(FactorQuanlity):
    def __init__(self):
        super().__init__('oprationcashflowratioq')

    def calculate(self, date):
        report_period = ba.nearest_report_period(date)[0]
        ocf = ba.Stock.cashflow_sheet(report_period, report_period,
            fields='net_cash_flows_oper_act').droplevel(0).net_cash_flows_oper_act
        np = ba.Stock.income_sheet(report_period, report_period,
            fields='net_profit_excl_min_int_inc').droplevel(0).net_profit_excl_min_int_inc
        self.factor = ocf / np

class OperationCashflowRatioTTM(FactorQuanlity):
    def __init__(self):
        super().__init__('oprationcashflowratiottm')
    
    def calculate(self, date):
        ocf = ba.Stock.pit_financial(date, date,
            fields='s_dfa_operatecashflow_ttm').droplevel(0).s_dfa_operatecashflow_ttm
        np = ba.Stock.pit_financial(date, date,
            fields='s_dfa_profit_ttm').droplevel(0).s_dfa_profit_ttm
        self.factor = ocf / np


if __name__ == "__main__":
    factor = OperationCashflowRatioTTM()
    print(factor('20200106'))