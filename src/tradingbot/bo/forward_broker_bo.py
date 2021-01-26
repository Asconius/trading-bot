from decimal import Decimal
from typing import Dict

from tradingbot.bo.broker_bo import BrokerBO
from tradingbot.bo.inventory_bo import InventoryBO
from tradingbot.dao.forward_dao import ForwardDAO
from tradingbot.enums.strategy_enum import StrategyEnum


class ForwardBrokerBO(BrokerBO):

    def __init__(self, cash: Decimal, fee: Decimal, inventory: Dict[str, InventoryBO],
                 strategy: StrategyEnum) -> None:
        super().__init__(cash, fee, inventory)
        self.strategy = strategy

    def buy(self, symbol: str, price: Decimal, number: Decimal) -> bool:
        success = super().buy(symbol, price, number)
        if success:
            ForwardDAO.create_buy(symbol, price, number, self._cash, self.strategy)
        return success

    def sell(self, symbol: str, price: Decimal, number: Decimal) -> bool:
        success = super().sell(symbol, price, number)
        if success:
            ForwardDAO.create_sell(symbol, price, number, self._cash, self.strategy)
        return success
