from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytz

from src import db
from src.dao.forward_dao import ForwardDAO
from src.enums.strategy_enum import StrategyEnum
from tests.base_test_case import BaseTestCase


class ForwardDAOTestCase(BaseTestCase):
    YOUNG_DATE = pytz.utc.localize(datetime.fromisoformat('2011-11-04T00:00:00'))
    OLD_DATE = pytz.utc.localize(datetime.fromisoformat('2011-11-03T00:00:00'))

    @classmethod
    def setUpClass(cls):
        db.create_all()

    @patch('src.utils.utils.Utils.now')
    def setUp(self, now):
        self.truncate_tables()
        now.return_value = self.YOUNG_DATE
        ForwardDAO.create_buy('AAA', Decimal('100'), Decimal('4'), Decimal('10'), StrategyEnum.COUNTER_CYCLICAL)
        now.return_value = self.OLD_DATE
        ForwardDAO.create_sell('AAA', Decimal('101'), Decimal('5'), Decimal('11'), StrategyEnum.COUNTER_CYCLICAL)

    def test_read_all(self):
        rows = ForwardDAO.read_all()
        self.assertEqual(len(rows), 2)

    def test_read_filter_by_strategy_and_max_timestamp(self):
        latest_date = ForwardDAO.read_filter_by_strategy_and_max_timestamp(StrategyEnum.COUNTER_CYCLICAL)
        self.assertEqual(latest_date, self.YOUNG_DATE)
