from tests.base_test_case import BaseTestCase
from tradingbot import Utils
from tradingbot.converter.attempt_dto_converter import AttemptDTOConverter
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.entity.evaluation_entity import EvaluationEntity


class AttemptDTOConverterTestCase(BaseTestCase):
    def test_from_evaluation(self):
        evaluation = EvaluationEntity()
        Utils.set_attributes(evaluation, amount_buy=2, distance_buy=3, delta_buy=4, amount_sell=5, distance_sell=6,
                             delta_sell=7)
        attempt = AttemptDTOConverter.from_evaluation(evaluation)
        self.assertIsInstance(attempt, AttemptDTO)
        self.assert_attributes(attempt, amount_buy=2, distance_buy=3, delta_buy=4, amount_sell=5, distance_sell=6,
                               delta_sell=7)
