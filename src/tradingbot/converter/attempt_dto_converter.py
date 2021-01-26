from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.entity.evaluation_entity import EvaluationEntity


class AttemptDTOConverter:

    @staticmethod
    def from_evaluation(evaluation: EvaluationEntity) -> AttemptDTO:
        return AttemptDTO(evaluation.amount_buy, evaluation.distance_buy, evaluation.delta_buy,
                          evaluation.amount_sell, evaluation.distance_sell, evaluation.delta_sell)
