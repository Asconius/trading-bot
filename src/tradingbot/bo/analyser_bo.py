from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Callable

from tradingbot.bo.broker_bo import BrokerBO
from tradingbot.bo.intraday_bo import IntradayBO
from tradingbot.bo.statistic_bo import StatisticBO
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.entity.intraday_entity import IntradayEntity
from tradingbot.enums.action_enum import ActionEnum


class AnalyserBO:

    @staticmethod
    def analyse(intraday_list: List[IntradayEntity], strategy: Callable, broker: BrokerBO,
                statistic: StatisticBO = None, attempt: AttemptDTO = None,
                latest_date_dict: Dict[str, str] = None) -> StatisticBO:
        intraday_list = IntradayBO.sort_by_date(intraday_list)
        grouped: Dict[str, List[IntradayEntity]] = IntradayBO.group_by_symbol(intraday_list)
        for intraday in intraday_list:
            symbol: str = intraday.symbol
            date: datetime = intraday.date
            if latest_date_dict is not None and latest_date_dict[symbol] != date:
                continue
            price: Decimal = intraday.close
            action, number = strategy(grouped[symbol], date, attempt)
            buy: bool = False
            sell: bool = False
            if action is ActionEnum.BUY:
                buy = broker.buy(symbol, price, number)
            elif action is ActionEnum.SELL:
                sell = broker.sell(symbol, price, number)
            else:
                broker.update(symbol, price)
            if statistic is not None:
                statistic.plot(date, symbol, price, buy, sell)
                statistic.test(action, number, symbol, price)
                statistic.log(action, date, symbol, price)
        return statistic
