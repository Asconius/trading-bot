from datetime import datetime
from unittest.mock import patch

from pandas import to_datetime, date_range
from pytz import timezone

from src import db, Utils
from src.bo.intraday_bo import IntradayBO
from src.common.constants import US_EASTERN
from src.dao.intraday_dao import IntradayDAO
from src.dao.stock_dao import StockDAO
from src.entity.intraday_entity import IntradayEntity
from tests.base_test_case import BaseTestCase


class IntradayBOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        self.truncate_tables()

    def test_sort_by_date(self):
        intraday_list = [IntradayEntity() for _ in range(10)]
        indices = [8, 1, 4, 2, 9, 5, 0, 7, 3, 6]
        dates = date_range(end='2020-01-01', periods=len(intraday_list)).to_pydatetime().tolist()
        for index, date in zip(indices, dates):
            Utils.set_attributes(intraday_list[index], date=self.create_datetime(date))
        actual_list = IntradayBO.sort_by_date(intraday_list)
        for intraday, date in zip(actual_list, dates):
            self.assertEqual(intraday.date, self.create_datetime(date))
        self.assertEqual(actual_list[0].date, self.create_datetime('2019-12-23 00:00:00'))
        self.assertEqual(actual_list[9].date, self.create_datetime('2020-01-01 00:00:00'))

    def test_group_by_symbol(self):
        intraday_list = self.create_default_intraday_list()
        grouped = IntradayBO.group_by_symbol(intraday_list)
        for symbol, group in grouped.items():
            for intraday in group:
                self.assertEqual(intraday.symbol, symbol)

    @patch('alpha_vantage.timeseries.TimeSeries.get_intraday_extended')
    @patch('src.bo.stock_bo.StockBO.isin')
    def test_update(self, isin, intraday):
        isin.return_value = 'isin'
        intraday.return_value = self.get_intraday_csv('BBB')
        StockDAO.create_if_not_exists(('AAA',))
        date = datetime.fromisoformat('2020-02-03')
        self.persist_intraday('AAA', date, 500, 500, 500, 500, 500)
        with patch('alpha_vantage.timeseries.TimeSeries.__init__', return_value=None):
            IntradayBO.update(('AAA', 'BBB',))
        self.assertEqual(intraday.call_count, 24)
        self.assertEqual(isin.call_count, 3)
        rows = IntradayDAO.read_order_by_date_asc()
        self.assertEqual(len(rows), 11)
        dates = date_range(end='2020-02-02', periods=10).to_pydatetime().tolist()
        for i in range(len(rows) - 1):
            self.assert_attributes(rows[i], date=timezone(US_EASTERN).localize(dates[i]),
                                   open=500, high=500, low=500, close=500, volume=500, symbol='BBB')
        self.assert_attributes(rows[10], date=timezone(US_EASTERN).localize(date),
                               open=500, high=500, low=500, close=500, volume=500, symbol='AAA')

    @patch('alpha_vantage.timeseries.TimeSeries.get_intraday')
    @patch('src.bo.stock_bo.StockBO.isin')
    def test_update_all_available(self, isin, intraday):
        isin.return_value = 'isin'
        intraday.return_value = self.get_intraday()
        StockDAO.create_if_not_exists(('AAA',))
        self.persist_intraday('AAA', self.create_datetime('2011-11-04T23:00:00'), 500, 500, 500, 500, 500)
        StockDAO.create_if_not_exists(('BBB',))
        self.persist_intraday('BBB', self.create_datetime('2011-11-04T22:00:00'), 500, 500, 500, 500, 500)
        StockDAO.create_if_not_exists(('CCC',))
        self.persist_intraday('CCC', self.create_datetime('2011-11-03T23:00:00'), 500, 500, 500, 500, 500)
        with patch('alpha_vantage.timeseries.TimeSeries.__init__', return_value=None):
            IntradayBO.update(('AAA', 'BBB', 'CCC'))
        intraday.assert_called_with(symbol='CCC', outputsize='full')
        self.assertEqual(intraday.call_count, 24)
        rows = IntradayDAO.read_order_by_date_asc()
        self.assertEqual(len(rows), 13)
        dates = date_range('1/1/2000', periods=10)
        for i in range(len(rows) - 3):
            date = timezone(US_EASTERN).localize(to_datetime(dates[i], format='%d%b%Y:%H:%M:%S.%f'))
            self.assert_attributes(rows[i], date=date, open=500, high=500, low=500, close=500, volume=500,
                                   symbol='CCC')
        self.assert_attributes(rows[10], date=self.create_datetime('2011-11-03T23:00:00'), open=500, high=500,
                               low=500, close=500, volume=500, symbol='CCC')
        self.assert_attributes(rows[11], date=self.create_datetime('2011-11-04T22:00:00'), open=500, high=500,
                               low=500, close=500, volume=500, symbol='BBB')
        self.assert_attributes(rows[12], date=self.create_datetime('2011-11-04T23:00:00'), open=500, high=500,
                               low=500, close=500, volume=500, symbol='AAA')
