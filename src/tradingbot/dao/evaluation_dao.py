from decimal import Decimal
from typing import List

from tradingbot.dao.base_dao import BaseDAO
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.entity.evaluation_entity import EvaluationEntity
from tradingbot.enums.strategy_enum import StrategyEnum
from tradingbot.utils.utils import Utils


class EvaluationDAO(BaseDAO):

    @classmethod
    def create(cls, summation: Decimal, funds: str, attempt: AttemptDTO, strategy: StrategyEnum) -> None:
        evaluation: EvaluationEntity = EvaluationEntity()
        evaluation.timestamp = Utils.now()
        evaluation.sum = str(summation)
        evaluation.funds = funds
        Utils.set_attributes(evaluation, amount_buy=str(attempt.amount_buy), distance_buy=str(attempt.distance_buy),
                             delta_buy=str(attempt.delta_buy), amount_sell=str(attempt.amount_sell),
                             distance_sell=str(attempt.distance_sell), delta_sell=str(attempt.delta_sell),
                             strategy=strategy)
        cls.persist(evaluation)

    @staticmethod
    def read_filter_by_strategy_order_by_sum(strategy: StrategyEnum) -> EvaluationEntity:
        return EvaluationEntity.query.filter_by(strategy=strategy).order_by(EvaluationEntity.sum.desc()).first()

    @staticmethod
    def read_filter_by_strategy_and_attempt(strategy: StrategyEnum, attempt: AttemptDTO) -> EvaluationEntity:
        return EvaluationEntity.query.filter_by(
            strategy=strategy).filter_by(
            amount_buy=attempt.amount_buy).filter_by(
            distance_buy=attempt.distance_buy).filter_by(
            delta_buy=attempt.delta_buy).filter_by(
            amount_sell=attempt.amount_sell).filter_by(
            distance_sell=attempt.distance_sell).filter_by(
            delta_sell=attempt.delta_sell).first()

    @staticmethod
    def read_all() -> List[EvaluationEntity]:
        return EvaluationEntity.query.all()
