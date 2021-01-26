from datetime import datetime
from decimal import Decimal
from json import dumps
from random import choice
from typing import Dict, List, Tuple, Any

from tradingbot.bo.analyser_bo import AnalyserBO
from tradingbot.bo.broker_bo import BrokerBO
from tradingbot.bo.forward_broker_bo import ForwardBrokerBO
from tradingbot.bo.inventory_bo import InventoryBO
from tradingbot.bo.portfolio_bo import PortfolioBO
from tradingbot.bo.statistic_bo import StatisticBO
from tradingbot.common.constants import ZERO
from tradingbot.converter.attempt_dto_converter import AttemptDTOConverter
from tradingbot.dao.configuration_dao import ConfigurationDAO
from tradingbot.dao.evaluation_dao import EvaluationDAO
from tradingbot.dao.forward_dao import ForwardDAO
from tradingbot.dao.intraday_dao import IntradayDAO
from tradingbot.dto.account_dto import AccountDTO
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.entity.evaluation_entity import EvaluationEntity
from tradingbot.entity.forward_entity import ForwardEntity
from tradingbot.entity.intraday_entity import IntradayEntity
from tradingbot.enums.action_enum import ActionEnum
from tradingbot.enums.configuration_enum import ConfigurationEnum
from tradingbot.enums.strategy_enum import StrategyEnum
from tradingbot.utils.utils import Utils


class ForwardBO:

    @classmethod
    def start(cls, portfolio: List[str]) -> None:
        latest_date: datetime = ForwardDAO.read_filter_by_strategy_and_max_timestamp(StrategyEnum.COUNTER_CYCLICAL)
        strategy: StrategyEnum = choice(list(StrategyEnum))
        evaluation: EvaluationEntity = EvaluationDAO.read_filter_by_strategy_order_by_sum(strategy)
        if evaluation is None or Utils.is_today(latest_date) or not Utils.is_working_day_ny():
            return
        read_latest_date: List[List[Any]] = IntradayDAO.read_latest_date()
        latest_date_dict: Dict[str, str] = {r[1]: r[0] for r in read_latest_date}
        intraday_list: List[IntradayEntity] = IntradayDAO.read(portfolio)
        inventory, cash, fee = cls.init(strategy)
        broker: BrokerBO = ForwardBrokerBO(cash, fee, inventory, strategy)
        statistic: StatisticBO = StatisticBO('forward')
        attempt: AttemptDTO = AttemptDTOConverter.from_evaluation(evaluation)
        statistic: StatisticBO = AnalyserBO.analyse(intraday_list, strategy.function, broker, statistic,
                                                    attempt, latest_date_dict)
        log_data_without_action_none: List[Dict[str, Any]] = statistic.log_data_without_action_none()
        if len(statistic.log_data_without_action_none()) > 0:
            Utils.send_mail(dumps(log_data_without_action_none, indent=4, sort_keys=True, default=str))

    @staticmethod
    def init(strategy: StrategyEnum) -> Tuple[Dict[str, InventoryBO], Decimal, Decimal]:
        cash: Decimal = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.FORWARD_CASH.identifier).value
        fee: Decimal = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.OPTIMIZATION_FEE.identifier).value
        forward_list: List[ForwardEntity] = ForwardDAO.read_filter_by_strategy(strategy)
        broker = BrokerBO(cash, fee)
        for forward in forward_list:
            if forward.action is ActionEnum.BUY:
                broker.buy(forward.symbol, forward.price, forward.number)
            elif forward.action is ActionEnum.SELL:
                broker.sell(forward.symbol, forward.price, forward.number)
        return broker.inventory, broker.cash, fee

    @staticmethod
    def update(inventory: Dict[str, InventoryBO], cash: Decimal) -> Tuple[Dict[str, InventoryBO], Decimal, Decimal]:
        total: Decimal = ZERO
        total_value: Decimal = ZERO
        for symbol, entry in inventory.items():
            intraday: IntradayEntity = IntradayDAO.read_filter_by_symbol_first(symbol)
            if intraday is None:
                continue
            entry.price = Decimal(intraday.close)
            total_value += entry.value()
        total += cash + total_value
        return inventory, total_value, total

    @classmethod
    def group_by_strategy(cls) -> Dict[StrategyEnum, List[ForwardEntity]]:
        forward_list: List[ForwardEntity] = ForwardDAO.read_all()
        return {b: [a for a in forward_list if a.strategy == b]
                for b in set(map(lambda b: b.strategy, forward_list))}

    @classmethod
    def get_accounts(cls) -> Dict[StrategyEnum, AccountDTO]:
        account_dict: Dict[StrategyEnum, AccountDTO] = {}
        for strategy in list(StrategyEnum):
            inventory, cash, _ = cls.init(strategy)
            inventory, total_value, total = cls.update(inventory, cash)
            account: AccountDTO = AccountDTO(inventory, cash, total_value, total)
            account_dict[strategy] = account
        return account_dict


if __name__ == '__main__':
    ForwardBO.start(PortfolioBO.forward_portfolio(100))
