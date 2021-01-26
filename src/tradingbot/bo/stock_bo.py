from re import search

from requests import get

from tradingbot.common.constants import EMPTY


class StockBO:

    @staticmethod
    def isin(symbol: str) -> str:
        url = 'https://markets.businessinsider.com/ajax/' \
              'SearchController_Suggest?max_results=25&query=%s' \
              % symbol
        data = get(url=url).text

        match = search('([A-Z]{2})([A-Z0-9]{9})([0-9])', data)
        return EMPTY if match is None else match.group(0)
