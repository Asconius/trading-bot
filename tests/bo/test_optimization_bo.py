from decimal import Decimal
from unittest.mock import patch

from src import db
from src.bo.configuration_bo import ConfigurationBO
from src.bo.optimization_bo import OptimizationBO
from src.common.constants import ZERO
from src.dao.evaluation_dao import EvaluationDAO
from src.dto.attempt_dto import AttemptDTO
from src.entity.evaluation_entity import EvaluationEntity
from src.enums.strategy_enum import StrategyEnum
from tests.base_test_case import BaseTestCase


class OptimizationBOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        self.truncate_tables()
        ConfigurationBO.init()

    @patch('src.utils.utils.Utils.negation')
    @patch('src.utils.utils.Utils.inverse')
    def test_optimise(self, negation, inverse):
        negation.return_value = ZERO
        inverse.return_value = ZERO
        rows = EvaluationDAO.read_all()
        self.assertEqual(len(rows), 0)
        OptimizationBO.optimise([self.create_default_intraday_list()], StrategyEnum.COUNTER_CYCLICAL)
        evaluation = EvaluationDAO.read_filter_by_strategy_order_by_sum(StrategyEnum.COUNTER_CYCLICAL)
        self.assert_attributes(evaluation, sum=Decimal('185266.8'), funds='185266.8', amount_buy=Decimal('1000'),
                               amount_sell=Decimal('1000'), delta_buy=Decimal('1.5'), delta_sell=Decimal('1.5'),
                               distance_buy=Decimal('30'), distance_sell=Decimal('30'))

    @patch('src.bo.optimization_bo.choice')
    @patch('src.utils.utils.Utils.negation')
    @patch('src.utils.utils.Utils.inverse')
    def test_start(self, inverse, negation, choice):
        negation.return_value = Decimal('1')
        inverse.return_value = Decimal('1')
        choice.return_value = StrategyEnum.COUNTER_CYCLICAL
        attempt = AttemptDTO(Decimal('1000'), Decimal('10'), Decimal('0.25'), Decimal('1000'), Decimal('10'),
                             Decimal('0.25'))
        EvaluationDAO.create(Decimal('10000'), 'second', attempt, StrategyEnum.COUNTER_CYCLICAL)
        self.persist_default_intraday()
        OptimizationBO.start(['AAA', 'BBB', 'CCC'], 3, 1)
        evaluation = EvaluationDAO.read_filter_by_strategy_order_by_sum(StrategyEnum.COUNTER_CYCLICAL)
        self.assertIsInstance(evaluation, EvaluationEntity)
        self.assert_attributes(evaluation, sum=Decimal('235112.5'), funds='235112.5', amount_buy=Decimal('2000'),
                               amount_sell=Decimal('2000'), delta_buy=Decimal('0.5'), delta_sell=Decimal('0.5'),
                               distance_buy=Decimal('20'), distance_sell=Decimal('20'),
                               strategy=StrategyEnum.COUNTER_CYCLICAL)
