from typing import List, Dict

from src.dao.evaluation_dao import EvaluationDAO
from src.entity.evaluation_entity import EvaluationEntity
from src.enums.strategy_enum import StrategyEnum


class EvaluationBO:

    @staticmethod
    def group_by_strategy() -> Dict[StrategyEnum, List[EvaluationEntity]]:
        evaluation_list: List[EvaluationEntity] = EvaluationDAO.read_all()
        return {b: [a for a in evaluation_list if a.strategy == b]
                for b in set(map(lambda b: b.strategy, evaluation_list))}
