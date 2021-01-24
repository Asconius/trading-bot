import json
import re
from typing import List, Tuple, Dict

import lxml.html as lh
import requests
from fake_useragent import UserAgent
from requests import Response


class Portfolio:

    @staticmethod
    def berkshire_hathaway_cnbc() -> Tuple[str]:
        url: str = 'https://docs.google.com/spreadsheet/tq?key=0AvnqqjtntdHRdENTQ283OGZTUWVMejRGTUVjZXphWlE'
        headers: Dict[str, str] = {'User-Agent': UserAgent().chrome}
        page: Response = requests.get(url, headers=headers)
        content: str = re.search(r'\((.*?)\)', page.text).group(1)
        data: Dict[str, Dict[str, List[str]]] = json.loads(content)
        return tuple(
            map(lambda e: str(e['c'][1]['v']), list(filter(lambda x: x['c'][1] is not None, data['table']['rows']))))

    @staticmethod
    def berkshire_hathaway_yahoo() -> Tuple[str]:
        url: str = 'https://finance.yahoo.com/u/yahoo-finance/watchlists/the-berkshire-hathaway-portfolio'
        headers: Dict[str, str] = {'User-Agent': UserAgent().chrome}
        page: Response = requests.get(url, headers=headers)
        doc = lh.fromstring(page.content)
        elements: List[lh.HtmlElement] = doc.xpath(
            '//*[@id="Col1-0-WatchlistDetail-Proxy"]/div/section[3]/div/div/table/tbody/tr/td[1]')
        return tuple(map(lambda e: str(e.text_content()), elements))

    @staticmethod
    def berkshire_hathaway_wikipedia() -> Tuple[str]:
        url: str = 'https://en.wikipedia.org/wiki/List_of_assets_owned_by_Berkshire_Hathaway'
        headers: Dict[str, str] = {'User-Agent': UserAgent().chrome}
        page: Response = requests.get(url, headers=headers)
        doc = lh.fromstring(page.content)
        elements = doc.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr/td[2]')
        return tuple(map(lambda e: re.sub(r'^.*?:', '', e.text_content()).strip(), elements))


if __name__ == '__main__':
    symbols: Tuple[str] = Portfolio.berkshire_hathaway_wikipedia()
    print(len(symbols))
    for symbol in symbols:
        print(symbol)
