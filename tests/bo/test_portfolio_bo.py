from unittest.mock import patch

from tests.base_test_case import BaseTestCase
from tradingbot import db
from tradingbot.bo.portfolio_bo import PortfolioBO
from tradingbot.dao.portfolio_dao import PortfolioDAO
from tradingbot.dao.stock_dao import StockDAO
from tradingbot.enums.mode_enum import ModeEnum


class PortfolioBOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        self.truncate_tables()

    def tearDown(self):
        self.truncate_tables()

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_forward_portfolio(self, isin):
        self.__init_database(isin)
        portfolio = PortfolioBO.forward_portfolio(100)
        self.assertEqual(len(portfolio), 2)
        self.assertEqual(portfolio[0], 'symbol2')
        self.assertEqual(portfolio[1], 'symbol1')

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_backward_portfolio(self, isin):
        self.__init_database(isin)
        portfolio = PortfolioBO.backward_portfolio(100)
        self.assertEqual(len(portfolio), 2)
        self.assertEqual(portfolio[0], 'symbol4')
        self.assertEqual(portfolio[1], 'symbol3')

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_backward_forward_portfolio(self, isin):
        self.__init_database(isin)
        portfolio = PortfolioBO.backward_forward_portfolio()
        self.assertEqual(len(portfolio), 4)
        self.assertEqual(portfolio[0], 'symbol2')
        self.assertEqual(portfolio[1], 'symbol1')
        self.assertEqual(portfolio[2], 'symbol4')
        self.assertEqual(portfolio[3], 'symbol3')

    @patch('tradingbot.bo.portfolio_bo.tickers_sp500')
    @patch('tradingbot.bo.portfolio_bo.tickers_nasdaq')
    @patch('tradingbot.dao.stock_dao.StockDAO.update')
    def test_init(self, update, tickers_nasdaq, tickers_sp500):
        symbol_list = ('FFF', 'BBB', 'DDD', 'GGG', 'CCC', 'AAA', 'HHH', 'EEE')
        tickers_sp500.return_value = ('AAA', 'BBB', 'CCC', 'DDD')
        tickers_nasdaq.return_value = ('EEE', 'FFF', 'GGG', 'HHH')
        PortfolioBO.init()
        portfolio = PortfolioBO.forward_portfolio(100)
        self.assertEqual(len(portfolio), 8)
        for p, symbol in zip(portfolio, symbol_list):
            self.assertEqual(p, symbol)
        portfolio = PortfolioBO.backward_portfolio(100)
        self.assertEqual(len(portfolio), 8)
        for p, symbol in zip(portfolio, symbol_list):
            self.assertEqual(p, symbol)
        portfolio = PortfolioBO.backward_forward_portfolio()
        self.assertEqual(len(portfolio), 16)
        for p, symbol in zip(portfolio, symbol_list * 2):
            self.assertEqual(p, symbol)
        update.assert_called_once_with(tuple(sorted(symbol_list)))

    @patch('tradingbot.bo.stock_bo.StockBO.isin')
    def test_update(self, isin):
        isin.return_value = 'isin'
        PortfolioBO.update('AAA', ModeEnum.BACKWARD)
        portfolio = PortfolioBO.read()
        self.assertEqual(len(portfolio), 1)
        self.assert_attributes(portfolio[0], symbol='AAA', mode=ModeEnum.BACKWARD)
        PortfolioBO.delete('AAA')
        portfolio = PortfolioBO.read_filter_by_symbol_isin('AAA')
        self.assertIsNone(portfolio)

    @staticmethod
    def __init_database(isin):
        isin.return_value = 'isin'
        StockDAO.update(('symbol1', 'symbol2', 'symbol3', 'symbol4',))
        PortfolioDAO.create('symbol1', ModeEnum.FORWARD)
        PortfolioDAO.create('symbol2', ModeEnum.FORWARD)
        PortfolioDAO.create('symbol3', ModeEnum.BACKWARD)
        PortfolioDAO.create('symbol4', ModeEnum.BACKWARD)
