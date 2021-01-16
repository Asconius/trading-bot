import copy
from decimal import Decimal
from typing import Tuple, List, NoReturn

from pandas import DataFrame

from src.bo.analyser_bo import AnalyserBO
from src.bo.broker_bo import BrokerBO
from src.bo.portfolio_bo import PortfolioBO
from src.bo.statistic_bo import StatisticBO
from src.bo.strategy_bo import StrategyBO
from src.common.constants import INFINITY, ZERO
from src.converter.attempt_dto_converter import AttemptDTOConverter
from src.dao.configuration_dao import ConfigurationDAO
from src.dao.evaluation_dao import EvaluationDAO
from src.dao.intraday_dao import IntradayDAO
from src.dto.attempt_dto import AttemptDTO
from src.entity.evaluation_entity import EvaluationEntity
from src.enums.configuration_enum import ConfigurationEnum
from src.utils.utils import Utils


# noinspection DuplicatedCode
class OptimizationBO:

    @staticmethod
    def optimise(tables: List[DataFrame]) -> NoReturn:
        cash: Decimal = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.OPTIMIZATION_CASH.identifier).value
        fee: Decimal = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.OPTIMIZATION_FEE.identifier).value
        evaluation: EvaluationEntity = EvaluationDAO.read_order_by_sum()
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

            evaluation: EvaluationEntity = EvaluationDAO.read_attempt(evaluation_attempt)
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
                EvaluationDAO.create(evaluation_sum, ','.join(map(str, analysis_funds)), evaluation_attempt)

    @classmethod
    def start(cls, portfolio: List[str], number: int, group_number: int) -> NoReturn:
        group_size: int = int(number / group_number)
        groups: Tuple[Tuple[str]] = Utils.group(group_size, portfolio[:number])
        cls.optimise(IntradayDAO.dataframe_group(groups))


if __name__ == '__main__':
    OptimizationBO.start(PortfolioBO.backward_portfolio(), 100, 4)
