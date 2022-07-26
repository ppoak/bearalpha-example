import bearalpha as ba


class Grid(ba.Indicator):
    lines = ('grid', 'level1', 'level2', 'level3', 'level4', 'level5')
    params = (('period', 10),)
    plotinfo = dict(subplot=False)
    plotlines = dict(grid=dict(_method='bar'))

    def __init__(self):
        self.high = ba.indicators.Highest(self.data.high, period=self.p.period)
        self.low = ba.indicators.Lowest(self.data.low, period=self.p.period)
        self.lines.gridlevel = [(self.high - self.low) * i / 5 + self.low for i in range(1, 5)]
        self.lines.level1 = self.lines.gridlevel[0]
        self.lines.level2 = self.lines.gridlevel[1]
        self.lines.level3 = self.lines.gridlevel[2]
        self.lines.level4 = self.lines.gridlevel[3]
        self.lines.grid = ba.Sum(*[self.data.close > self.gridlevel[i] for i in range(len(self.gridlevel))])
