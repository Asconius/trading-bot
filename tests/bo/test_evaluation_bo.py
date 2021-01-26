from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from pandas import date_range

from tests.base_test_case import BaseTestCase
from tradingbot import db
from tradingbot.bo.evaluation_bo import EvaluationBO
from tradingbot.dao.evaluation_dao import EvaluationDAO
from tradingbot.dto.attempt_dto import AttemptDTO
from tradingbot.enums.strategy_enum import StrategyEnum


class EvaluationBOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    @patch('tradingbot.utils.utils.Utils.now')
    def setUp(self, now):
        self.truncate_tables()
        dates = date_range('1/1/2000', periods=5)
        for i in range(len(dates)):
            attempt = AttemptDTO(Decimal(i), Decimal(i), Decimal(i), Decimal(i), Decimal(i), Decimal(i))
            now.return_value = self.create_datetime(dates[i])
            EvaluationDAO.create(Decimal(i), 'first', attempt, strategy=StrategyEnum.COUNTER_CYCLICAL)
            now.return_value = self.create_datetime(dates[i] + timedelta(minutes=1))
            attempt = AttemptDTO(Decimal(i), Decimal(i), Decimal(i), Decimal(i), Decimal(i), Decimal(i))
            EvaluationDAO.create(Decimal(i), 'second', attempt, strategy=StrategyEnum.VOLUME_TRADING)

    def test_group_by_strategy(self):
        grouped = EvaluationBO.group_by_strategy()
        self.assertEqual(len(grouped), 2)
        for group in grouped.values():
            self.assertEqual(len(group), 5)
        for evaluation in grouped[StrategyEnum.COUNTER_CYCLICAL]:
            self.assertEqual(evaluation.strategy, StrategyEnum.COUNTER_CYCLICAL)
        for evaluation in grouped[StrategyEnum.VOLUME_TRADING]:
            self.assertEqual(evaluation.strategy, StrategyEnum.VOLUME_TRADING)
