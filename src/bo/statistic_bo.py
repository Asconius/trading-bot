from datetime import datetime
from decimal import Decimal
from typing import List, Dict


class StatisticBO:

    def __init__(self, name: str = 'statistic') -> None:
        self.name: str = name
        self.test_data: List[Dict[str, any]] = []

    def plot(self, date: datetime, ticker: str, price: Decimal, buy: bool, sell: bool) -> None:
        pass  # Do nothing

    def test(self, action: str, number: Decimal, ticker: str, price: Decimal) -> None:
        self.test_data.append({'action': action, 'number': number, 'ticker': ticker, 'price': price})

    def log(self, action: str, date: datetime, ticker: str, price: Decimal, buy: bool, sell: bool) -> None:
        pass  # Do nothing
