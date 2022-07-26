from .pricevolume import (
    HAlpha,
    HBeta,
    Momentum,
    WeightedMomentum,
    ExpWeightedMomentum,
    LogPrice,
    Amplitude,
    PriceVolumeMeasuredSentiment,
    ResidualMomentum,
    AR,
    Bias,
)

from .liquidity import (
    NonLiquidityImpact,
    TurnoverMA,
    TurnoverProp,
    AmountPerVolume,
    AmountPerChangeMA,
)


BARRASTYLE = {
    "halpha": {
        "factor": HAlpha,
        "args": (30, ),
    },
    "hbeta": {
        "factor": HBeta,
        "args": (30, ),
    },
    "momentum": {
        "factor": Momentum,
        "args": (20, ),
    },
    "weightedmomentum": {
        "factor": WeightedMomentum,
        "args": (20, ),
    },
    "expweightedmomentum": {
        "factor": ExpWeightedMomentum,
        "args": (20, ),
    },
    "logprice": {
        "factor": LogPrice,
        "args": (),
    },
    "amplitude": {
        "factor": Amplitude,
        "args": (20, ),
    },
    "residualmomentum": {
        "factor": ResidualMomentum,
        "args": (20, ),
    },
    "ar": {
        "factor": AR,
        "args": (20, ),
    },
        "bias": {
        "factor": Bias,
        "args": (20, ),
    },

    "nonliquidityimpact": {
        "factor": NonLiquidityImpact,
        "args": (20, ),
    },
    "turnoverma": {
        "factor": TurnoverMA,
        "args": (20, ),
    },
    "turnoverprop": {
        "factor": TurnoverProp,
        "args": (10, 20),
    },
    "amountpervolume": {
        "factor": AmountPerVolume,
        "args": (20, ),
    },
    "amountperchangema": {
        "factor": AmountPerChangeMA,
        "args": (10, ),
    },
}