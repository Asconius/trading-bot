from decimal import Decimal
from operator import attrgetter
from typing import List, Dict, NoReturn, Optional

from flask import Request
from pandas import DataFrame

from src.common.constants import NAN
from src.dao.intraday_dao import IntradayDAO
from src.dao.stock_dao import StockDAO
from src.entity.intraday_entity import IntradayEntity
from src.entity.stock_entity import StockEntity


class IntradayEntityConverter:

    @staticmethod
    def from_file(request: Request) -> NoReturn:
        IntradayDAO.create_from_file(request.files['file'].read())

    @staticmethod
    def to_file() -> List[Dict[str, str]]:
        intraday_list: List[IntradayEntity] = IntradayDAO.read_order_by_date_asc()
        intraday_dict: List[Dict[str, str]] = list(map(lambda intraday: dict(list(map(lambda i: (
            str(i[0]), str(float(i[1])) if isinstance(i[1], Decimal) else str(i[1])), filter(
            lambda e: not e[0].startswith('_'), intraday.__dict__.items())))), sorted(
            intraday_list, key=attrgetter('symbol'))))
        return intraday_dict

    @staticmethod
    def to_dataframe(intraday_list: List[IntradayEntity], column: str = 'close') -> DataFrame:
        frame: DataFrame = DataFrame()
        for intraday in intraday_list:
            frame.at[intraday.date, intraday.symbol] = Decimal(getattr(intraday, column))
        return frame.fillna(NAN)

    @classmethod
    def to_html(cls) -> Optional[str]:
        stock_list: List[StockEntity] = StockDAO.read_symbol()
        symbols: List[str] = list(map(lambda stock: stock.symbol, stock_list))
        intraday_list: List[IntradayEntity] = IntradayDAO.read(symbols)
        return cls.to_dataframe(intraday_list).to_html(classes='data', header='true')
