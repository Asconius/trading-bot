import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytz

from src import db
from src.constants import US_EASTERN, UTC
from src.dao.dao import DAO
from src.dao.intraday_dao import IntradayDAO
from src.entity.intraday_entity import IntradayEntity
from src.utils.utils import Utils as Utilities
from tests.utils.utils import Utils


class IntradayDAOTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        Utils.truncate_tables()

    def test_init(self):
        data = {'date': ['2020-05-01 16:00:00', '2020-05-01 15:55:00'],
                '1. open': ['121.4000', '121.6703'],
                '2. high': ['121.8700', '121.8200'],
                '3. low': ['121.4000', '121.3900'],
                '4. close': ['121.8300', '121.3900'],
                '5. volume': ['219717', '119646']
                }
        frame = pd.DataFrame(data)
        for index, row in frame.iterrows():
            intraday = IntradayDAO.init(row, 'IBM', UTC)
            self.assertIsInstance(intraday, IntradayEntity)
            Utils.assert_attributes(intraday, date=pytz.utc.localize(datetime.fromisoformat(row['date'])),
                                    open=float(row['1. open']), high=float(row['2. high']), low=float(row['3. low']),
                                    close=float(row['4. close']), volume=float(row['5. volume']), ticker='IBM')

    def test_localize(self):
        date = datetime.fromisoformat('2011-11-04T00:00:00')
        eastern = pytz.timezone(US_EASTERN).localize(date)
        intraday = IntradayEntity()
        Utilities.set_attributes(intraday, date=eastern, open=1, high=1, low=1, close=1, volume=1, ticker='AAA')
        DAO.persist(intraday)
        intraday = IntradayDAO.read_filter_by_ticker_first('AAA')
        self.__assert_date(eastern, intraday, date)

    def test_eastern_utc(self):
        date = datetime.fromisoformat('2011-11-04T00:00:00')
        Utils.persist_intraday('AAA', date, 1, 1, 1, 1, 1)
        intraday = IntradayDAO.read_filter_by_ticker_first('AAA')
        eastern = pytz.timezone(US_EASTERN).localize(date)
        self.__assert_date(eastern, intraday, date)

    def __assert_date(self, eastern, intraday, date):
        utc = eastern.astimezone(pytz.utc)
        self.assertEqual(intraday.date, pytz.utc.localize(date + timedelta(hours=4)))
        self.assertEqual(intraday.date, utc)
        self.assertEqual(intraday.date.astimezone(pytz.timezone(US_EASTERN)), eastern)

    @patch('alpha_vantage.timeseries.TimeSeries.get_intraday')
    def test_create_ticker(self, intraday):
        intraday.return_value = Utils.get_intraday()
        with patch('alpha_vantage.timeseries.TimeSeries.__init__', return_value=None):
            IntradayDAO.create_ticker('AAA')
        rows = IntradayDAO.read_order_by_date_asc()
        self.assertEqual(len(rows), 10)
        date = pytz.utc.localize(datetime.fromisoformat('2000-01-01T05:00:00'))
        Utils.assert_attributes(rows[0], date=date, open=500, high=500, low=500, close=500, volume=500, ticker='AAA')


if __name__ == '__main__':
    unittest.main()
