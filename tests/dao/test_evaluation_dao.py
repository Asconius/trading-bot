from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytz

from src import db
from src.dao.evaluation_dao import EvaluationDAO
from src.dto.attempt_dto import AttemptDTO
from src.entity.evaluation_entity import EvaluationEntity
from src.enums.strategy_enum import StrategyEnum
from tests.base_test_case import BaseTestCase


class EvaluationDAOTestCase(BaseTestCase):
    YOUNG_DATE = pytz.utc.localize(datetime.fromisoformat('2011-11-04T00:00:00'))
    OLD_DATE = pytz.utc.localize(datetime.fromisoformat('2011-11-03T00:00:00'))

    @classmethod
    def setUpClass(cls):
        db.create_all()

    @patch('src.utils.utils.Utils.now')
    def setUp(self, now):
        self.truncate_tables()
        self.attempt = AttemptDTO(Decimal('1'), Decimal('2'), Decimal('3'), Decimal('4'), Decimal('5'), Decimal('6'))
        now.return_value = self.YOUNG_DATE
        EvaluationDAO.create(Decimal('1000'), 'first', self.attempt, strategy=StrategyEnum.COUNTER_CYCLICAL)
        now.return_value = self.OLD_DATE
        attempt = AttemptDTO(Decimal('11'), Decimal('22'), Decimal('33'), Decimal('44'), Decimal('55'), Decimal('66'))
        EvaluationDAO.create(Decimal('2000'), 'second', attempt, strategy=StrategyEnum.COUNTER_CYCLICAL)

    def test_read_all(self):
        rows = EvaluationDAO.read_all()
        self.assertEqual(len(rows), 2)

    def test_read_filter_by_strategy_order_by_sum(self):
        evaluation = EvaluationDAO.read_filter_by_strategy_order_by_sum(StrategyEnum.COUNTER_CYCLICAL)
        self.assertIsInstance(evaluation, EvaluationEntity)
        self.assert_attributes(evaluation, timestamp=self.OLD_DATE, sum=Decimal('2000'), funds='second',
                               amount_buy=Decimal('11'), distance_buy=Decimal('22'), delta_buy=Decimal('33'),
                               amount_sell=Decimal('44'), distance_sell=Decimal('55'), delta_sell=Decimal('66'))

    def test_read_filter_by_strategy_and_attempt(self):
        evaluation = EvaluationDAO.read_filter_by_strategy_and_attempt(StrategyEnum.COUNTER_CYCLICAL, self.attempt)
        self.assertIsInstance(evaluation, EvaluationEntity)
        self.assert_attributes(evaluation, timestamp=self.YOUNG_DATE, sum=Decimal('1000'), funds='first',
                               amount_buy=Decimal('1'), distance_buy=Decimal('2'), delta_buy=Decimal('3'),
                               amount_sell=Decimal('4'), distance_sell=Decimal('5'), delta_sell=Decimal('6'))
