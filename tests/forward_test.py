import math
import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src import db
from src.action import Action
from src.attempt import Attempt
from src.dao.dao import DAO
from src.dao.evaluation_dao import EvaluationDAO
from src.dao.forward_dao import ForwardDAO
from src.dao.intraday_dao import IntradayDAO
from src.entity.evaluation_entity import EvaluationEntity
from src.entity.forward_entity import ForwardEntity
from src.entity.intraday_entity import IntradayEntity
from src.forward import Forward
from tests.utils import Utils


class ForwardTestCase(unittest.TestCase):
    YOUNG_DATE = datetime.fromisoformat('2011-11-04T00:00:00')
    OLD_DATE = datetime.fromisoformat('2011-11-03T00:00:00')

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        EvaluationEntity.query.delete()
        IntradayEntity.query.delete()
        ForwardEntity.query.delete()

    @patch('src.utils.Utils.is_today')
    @patch('src.utils.Utils.is_working_day_ny')
    @patch('src.utils.Utils.now')
    def test_start(self, now, is_working_day_ny, is_today):
        is_today.return_value = False
        is_working_day_ny.return_value = True
        now.return_value = ForwardTestCase.OLD_DATE
        ForwardDAO.create_buy('AAA', 100.0, 10, 8996.1)
        ForwardDAO.create_buy('BBB', 100.0, 10, 7992.200000000001)
        now.return_value = datetime.fromisoformat('2011-11-04T00:00:00')
        EvaluationDAO.create(40000, '', Attempt())
        ForwardTestCase.__create_intraday()
        Forward.start()
        self.assertEqual(True, True)
        rows = ForwardDAO.read_all()
        self.assertEqual(len(rows), 3)
        self.__assert_forward(rows[0], Action.BUY, 8996.1, ForwardTestCase.OLD_DATE, 10, 100.0, 'AAA')
        self.__assert_forward(rows[1], Action.BUY, 7992.200000000001, ForwardTestCase.OLD_DATE, 10, 100.0, 'BBB')
        self.__assert_forward(rows[2], Action.SELL, 12988.300000000001, ForwardTestCase.YOUNG_DATE, 2, 500.0, 'AAA')

    def __assert_forward(self, forward, action, cash, date, number, price, ticker):
        self.assertEqual(forward.action, action)
        self.assertEqual(forward.cash, cash)
        self.assertEqual(forward.date, date)
        self.assertEqual(forward.number, number)
        self.assertEqual(forward.price, price)
        self.assertEqual(forward.ticker, ticker)

    @staticmethod
    def __create_intraday():
        frame = Utils.create_frame()
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                ticker = frame.columns[j]
                date = pd.to_datetime(frame.index.values[i], format='%d%b%Y:%H:%M:%S.%f')
                price = frame.iloc[i][j]
                if math.isnan(price):
                    continue
                data = [date, price, price, price, price, price]
                index = ['date', '1. open', '2. high', '3. low', '4. close', '5. volume']
                series = pd.Series(data, index=index, dtype=object)
                intraday = IntradayDAO.init(series, ticker)
                DAO.persist(intraday)


if __name__ == '__main__':
    unittest.main()
