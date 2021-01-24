import json
import logging
from datetime import datetime
from decimal import Decimal
from time import sleep
from typing import List, Tuple, Any, NoReturn, Final, Union

import pytz
from alpha_vantage.timeseries import TimeSeries
from pandas import Series
from sqlalchemy import func

from src import db
from src.common.constants import US_EASTERN, REQUEST_SLEEP
from src.dao.base_dao import BaseDAO
from src.entity.intraday_entity import IntradayEntity
from src.utils.utils import Utils


class IntradayDAO(BaseDAO):
    YEAR_RANGE: Final[int] = 2
    MONTH_RANGE: Final[int] = 12
    INTRADAY_COLUMN: Tuple[str] = ('date', '1. open', '2. high', '3. low', '4. close', '5. volume')
    INTRADAY_EXTENDED_COLUMN: Tuple[int] = tuple(range(6))

    @classmethod
    def create_symbol(cls, symbol: str) -> NoReturn:
        try:
            time_series = TimeSeries(output_format='pandas')
            frame, meta_data = time_series.get_intraday(symbol=symbol.replace('.', '-'), outputsize='full')
            frame = frame.reset_index()
            for index, row in frame.iterrows():
                intraday = cls.init(row, symbol, meta_data['6. Time Zone'])
                cls.persist(intraday)
        except ValueError as e:
            logging.exception(e)

    @classmethod
    def create_symbol_extended(cls, symbol: str) -> NoReturn:
        time_series = TimeSeries(output_format='csv')
        for year in range(cls.YEAR_RANGE):
            for month in range(cls.MONTH_RANGE):
                try:
                    s: str = 'year{}month{}'.format(year + 1, month + 1)
                    csv_reader, _ = time_series.get_intraday_extended(symbol, slice=s)
                    line_count: int = 0
                    for row in csv_reader:
                        if line_count > 0:
                            intraday = cls.init(row, symbol, US_EASTERN, cls.INTRADAY_EXTENDED_COLUMN)
                            cls.persist(intraday)
                        line_count += 1
                except ValueError as e:
                    logging.exception(e)
                    return
                if not Utils.is_test():
                    sleep(REQUEST_SLEEP)

    @classmethod
    def create_from_file(cls, content: str) -> NoReturn:
        rows = json.loads(content)
        for row in rows:
            intraday: IntradayEntity = IntradayEntity()
            Utils.set_attributes(intraday, date=datetime.fromisoformat(row['date']), open=Decimal(row['open']),
                                 high=Decimal(row['high']), low=Decimal(row['low']), close=Decimal(row['close']),
                                 volume=Decimal(row['volume']), symbol=row['symbol'])
            cls.persist(intraday)

    @staticmethod
    def read(portfolio: List[str]) -> List[IntradayEntity]:
        return IntradayEntity.query.filter(IntradayEntity.symbol.in_(portfolio)).order_by(
            IntradayEntity.date.asc()).all()

    @staticmethod
    def read_order_by_date_asc() -> List[IntradayEntity]:
        return IntradayEntity.query.order_by(IntradayEntity.date.asc()).all()

    @staticmethod
    def read_filter_by_symbol(symbol: str) -> List[IntradayEntity]:
        return IntradayEntity.query.filter_by(symbol=symbol).order_by(IntradayEntity.date.desc()).all()

    @staticmethod
    def read_filter_by_symbol_first(symbol: str) -> IntradayEntity:
        return IntradayEntity.query.filter_by(symbol=symbol).order_by(IntradayEntity.date.desc()).first()

    @staticmethod
    def read_latest_date() -> List[List[Any]]:
        return db.session.query(func.max(IntradayEntity.date), IntradayEntity.symbol).group_by(
            IntradayEntity.symbol).all()

    @classmethod
    def intraday_list_group(cls, group: Tuple[Tuple[str]]) -> List[List[IntradayEntity]]:
        return list(map(lambda g: cls.read(g), group))

    @staticmethod
    def init(row: Series, symbol: str, timezone: str,
             column: Tuple[Union[int, str]] = INTRADAY_COLUMN) -> IntradayEntity:
        intraday: IntradayEntity = IntradayEntity()
        Utils.set_attributes(intraday,
                             date=pytz.timezone(timezone).localize(datetime.fromisoformat(str(row[column[0]]))),
                             open=Decimal(row[column[1]]), high=Decimal(row[column[2]]), low=Decimal(row[column[3]]),
                             close=Decimal(row[column[4]]), volume=Decimal(row[column[5]]), symbol=symbol)
        return intraday


if __name__ == '__main__':
    IntradayDAO.create_symbol('aaa')
