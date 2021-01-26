from enum import Enum
from typing import Callable

from tradingbot.bo.strategy_bo import StrategyBO


class StrategyEnum(Enum):
    COUNTER_CYCLICAL = ('COUNTER_CYCLICAL', StrategyBO.counter_cyclical)
    VOLUME_TRADING = ('VOLUME_TRADING', StrategyBO.volume_trading)

    def __init__(self, identifier: str, function: Callable):
        self.identifier = identifier
        self.function = function
