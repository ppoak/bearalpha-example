import bearalpha as ba
from ..core import FactorBase

class FactorValuation(FactorBase):
    def __init__(self, name):
        super().__init__(name)
        self.klass = 'valuation'

class Ep(FactorValuation):
    def __init__(self):
        super().__init__('ep')
    
    def calculate(self, date):
        pe = ba.Stock.derivative_indicator(date, date,
            fields='s_val_pe_ttm').droplevel(0).s_val_pe_ttm
        self.factor = 1 / pe
    
class Epcut(FactorValuation):
    def __init__(self):
        super().__init__('epcut')
    
    def calculate(self, date):
        ecut = ba.Stock.pit_financial(date, date,
            fields='s_dfa_deductedprofit_ttm').\
            droplevel(0).s_dfa_deductedprofit_ttm
        mv = ba.Stock.derivative_indicator(date, date,
            fields='s_val_mv').droplevel(0).s_val_mv
        self.factor = ecut / mv
        
class Bp(FactorValuation):
    def __init__(self):
        super().__init__('bp')
    
    def calculate(self, date):
        pb = ba.Stock.derivative_indicator(date, date,
            fields='s_val_pb_new').droplevel(0).s_val_pb_new
        self.factor = 1 / pb

class Sp(FactorValuation):
    def __init__(self):
        super().__init__('sp')
    
    def calculate(self, date):
        ps = ba.Stock.derivative_indicator(date, date,
            fields='s_val_ps_ttm').droplevel(0).s_val_ps_ttm
        self.factor = 1 / ps

class Ncfp(FactorValuation):
    def __init__(self):
        super().__init__('ncfp')
    
    def calculate(self, date):
        pcfn = ba.Stock.derivative_indicator(date, date,
            fields='s_val_pcf_ncfttm').\
                droplevel(0).s_val_pcf_ncfttm
        self.factor = 1 / pcfn

class Ocfp(FactorValuation):
    def __init__(self):
        super().__init__('ocfp')
    
    def calculate(self, date):
        ocfn = ba.Stock.derivative_indicator(date, date,
            fields='s_val_pcf_ocfttm').\
                droplevel(0).s_val_pcf_ocfttm
        self.factor = 1 / ocfn

class Dp(FactorValuation):
    def __init__(self):
        super().__init__('dp')
    
    def calculate(self, date):
        pd = ba.Stock.derivative_indicator(date, date,
            fields='s_price_div_dps').\
                droplevel(0).s_price_div_dps
        self.factor = 1 / pd
    
class Gpe(FactorValuation):
    def __init__(self):
        super().__init__('gpe')
    
    def calculate(self, date):
        before = ba.Stock.nearby_n_trade_date(date, -252)
        ptoday = ba.Stock.derivative_indicator(date, date,
            fields='net_profit_parent_comp_ttm').\
                droplevel(0).net_profit_parent_comp_ttm
        pbefore = ba.Stock.derivative_indicator(before, before,
            fields='net_profit_parent_comp_ttm').\
                droplevel(0).net_profit_parent_comp_ttm
        pe = ba.Stock.derivative_indicator(date, date,
            fields='s_val_pe_ttm').\
                droplevel(0).s_val_pe_ttm
        self.factor = ((ptoday - pbefore) / pbefore) / pe


if __name__ == "__main__":
    factor = Gpe()
    print(factor('20200106'))