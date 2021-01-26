from unittest.mock import patch

from tests.base_test_case import BaseTestCase
from tradingbot import db
from tradingbot.dao.stock_dao import StockDAO


class StockDAOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        self.truncate_tables()

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_read_all(self, isin):
        isin.return_value = 'isin'
        StockDAO.update(('AAA',))
        result = StockDAO.read_all()
        self.assertEqual(result[0].symbol, 'AAA')
        self.assertEqual(result[0].isin, 'isin')

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_read_symbol(self, isin):
        isin.return_value = 'isin'
        portfolio = ('AAA',)
        StockDAO.create_if_not_exists(portfolio)
        result = StockDAO.read_symbol()
        self.assertEqual(result[0].symbol, 'AAA')

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_exception(self, isin):
        isin.return_value = 'isin'
        StockDAO.update((None,))
        result = StockDAO.read_all()
        self.assertListEqual(result, [])
