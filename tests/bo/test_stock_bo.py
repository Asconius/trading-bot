from unittest import TestCase
from unittest.mock import patch, Mock

from tradingbot.bo.stock_bo import StockBO


class StockBOTestCase(TestCase):
    @patch('tradingbot.bo.stock_bo.get')
    def test_isin(self, get):
        response = Mock()
        get.return_value = response
        setattr(response, 'text', '"Stocks", "AAA|US0378331005|AAA||AAA", ')
        isin = StockBO.isin('aaa')
        self.assertEqual(isin, 'US0378331005')
