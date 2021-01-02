from unittest import TestCase
from unittest.mock import patch, Mock

from src.bo.stock_bo import StockBO


class StockBOTestCase(TestCase):
    @patch('requests.get')
    def test_isin(self, get):
        response = Mock()
        get.return_value = response
        setattr(response, 'text', '"Stocks", "AAPL|US0378331005|AAPL||AAPL", ')
        isin = StockBO.isin('aapl')
        self.assertEqual(isin, 'US0378331005')
