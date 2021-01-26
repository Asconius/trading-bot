import copy
from decimal import Decimal
from random import choice
from typing import Tuple, List

from tradingbot.bo.analyser_bo import AnalyserBO
from tradingbot.bo.broker_bo import BrokerBO
from tradingbot.bo.portfolio_bo import PortfolioBO
from tradingbot.bo.statistic_bo import StatisticBO
from tradingbot.bo.strategy_bo import StrategyBO
from tradingbot.common.constants import INFINITY, ZERO
from tradingbot.converter.attempt_dto_converter import AttemptDTOConverter
from tradingbot.dao.configuration_dao import ConfigurationDAO
from tradingbot.dao.evaluation_dao import EvaluationDAO
from tradingbot.dao.intraday_dao import IntradayDAO
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.entity.evaluation_entity import EvaluationEntity
from tradingbot.entity.intraday_entity import IntradayEntity
from tradingbot.enums.configuration_enum import ConfigurationEnum
from tradingbot.enums.strategy_enum import StrategyEnum
from tradingbot.utils.utils import Utils


# noinspection DuplicatedCode
class OptimizationBO:

    @staticmethod
    def optimise(tables: List[List[IntradayEntity]], strategy: StrategyEnum) -> None:
        cash: Decimal = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.OPTIMIZATION_CASH.identifier).value
        fee: Decimal = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.OPTIMIZATION_FEE.identifier).value
        evaluation: EvaluationEntity = EvaluationDAO.read_filter_by_strategy_order_by_sum(strategy)
        if evaluation is None:
            attempt: AttemptDTO = AttemptDTO()
            optimise_sum: Decimal = cash * len(tables)
        else:
            attempt: AttemptDTO = AttemptDTOConverter.from_evaluation(evaluation)
            optimise_sum: Decimal = Decimal(evaluation.sum)
        while True:
            evaluation_attempt: AttemptDTO = copy.copy(attempt)
            evaluation_attempt.amount_buy += Utils.truncate(attempt.amount_buy * Utils.inverse()) * Utils.negation()
            evaluation_attempt.distance_buy += Utils.truncate(
                attempt.distance_buy * Utils.inverse()) * Utils.negation()
            evaluation_attempt.delta_buy += attempt.delta_buy * Utils.inverse() * Utils.negation()

            evaluation_attempt.amount_sell += Utils.truncate(attempt.amount_sell * Utils.inverse()) * Utils.negation()
            evaluation_attempt.distance_sell += Utils.truncate(
                attempt.distance_sell * Utils.inverse()) * Utils.negation()
            evaluation_attempt.delta_sell += attempt.delta_sell * Utils.inverse() * Utils.negation()

            start_tuple = (ZERO, ZERO, ZERO, ZERO, ZERO, ZERO)
            stop_tuple = (INFINITY, INFINITY, INFINITY, INFINITY, INFINITY, INFINITY)
            if not all([Utils.valid(start, value, stop) for start, value, stop in
                        zip(start_tuple, evaluation_attempt.__dict__.values(), stop_tuple)]):
                continue

            evaluation: EvaluationEntity = EvaluationDAO.read_filter_by_strategy_and_attempt(
                strategy, evaluation_attempt)
            if evaluation is None:
                break

        evaluation_sum: Decimal = ZERO
        analysis_funds: List[Decimal] = []
        table_number: int = len(tables)
        for i in range(table_number):
            analysis_number: int = i + 1
            statistic_name: str = 'statistic analysis{}'.format(analysis_number)
            statistic: StatisticBO = StatisticBO(statistic_name)
            broker: BrokerBO = BrokerBO(cash, fee)
            AnalyserBO.analyse(tables[i], StrategyBO.counter_cyclical, broker, statistic, evaluation_attempt)
            evaluation_sum += broker.funds()
            analysis_funds.append(broker.funds().normalize())
            if analysis_number == table_number and evaluation_sum > optimise_sum:
                EvaluationDAO.create(evaluation_sum, ','.join(map(str, analysis_funds)), evaluation_attempt, strategy)

    @classmethod
    def start(cls, portfolio: List[str], number: int, group_number: int) -> None:
        group_size: int = int(number / group_number)
        groups: Tuple[Tuple[str]] = Utils.group(group_size, portfolio[:number])
        strategy: StrategyEnum = choice(list(StrategyEnum))
        cls.optimise(IntradayDAO.intraday_list_group(groups), strategy)


if __name__ == '__main__':
    OptimizationBO.start(PortfolioBO.backward_portfolio(), 100, 4)
