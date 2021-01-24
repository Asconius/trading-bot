import copy
from datetime import datetime
from decimal import Decimal
from typing import Union
from unittest import TestCase

from numpy import full
from pandas import DataFrame, date_range
from pytz import timezone

from src import Utils
from src.common.constants import US_EASTERN, NAN
from src.dao.base_dao import BaseDAO
from src.dao.intraday_dao import IntradayDAO
from src.entity.configuration_entity import ConfigurationEntity
from src.entity.evaluation_entity import EvaluationEntity
from src.entity.forward_entity import ForwardEntity
from src.entity.intraday_entity import IntradayEntity
from src.entity.portfolio_entity import PortfolioEntity
from src.entity.stock_entity import StockEntity


class BaseTestCase(TestCase):

    def assert_attributes(self, assertable, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(getattr(assertable, key), value)

    def assert_items(self, assertable, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(value, assertable[key])

    @classmethod
    def persist_intraday(cls, symbol, date, o, high, low, close, volume):
        cls.__persist_get_intraday(date.replace(tzinfo=None), full((1, 5), [o, high, low, close, volume]), symbol)

    @classmethod
    def persist_default_intraday(cls):
        table_aaa = full((150, 5), Decimal(500))
        table_ccc = copy.copy(table_aaa)
        table_aaa[30:60] = table_aaa[90:120] = table_ccc[0:30] = table_ccc[60:90] = table_ccc[120:150] = Decimal(100)
        data = {'AAA': {'start': '1/1/2000', 'data': table_aaa},
                'BBB': {'start': '31/1/2000', 'data': full((120, 5), Decimal(500))},
                'CCC': {'start': '1/1/2000', 'data': table_ccc}}
        for key, value in data.items():
            cls.__persist_get_intraday(value['start'], value['data'], key)

    @classmethod
    def __persist_get_intraday(cls, start, data, symbol):
        frame, meta_data = cls.get_intraday(start, data)
        frame = frame.reset_index()
        for index, row in frame.iterrows():
            intraday = IntradayDAO.init(row, symbol, meta_data['6. Time Zone'])
            BaseDAO.persist(intraday)

    @staticmethod
    def get_intraday(start='1/1/2000', data=full((10, 5), Decimal(500))):
        dates = date_range(start, periods=len(data))
        columns = ['1. open', '2. high', '3. low', '4. close', '5. volume']
        frame = DataFrame(data, columns=columns)
        frame['date'] = dates
        frame.sort_index(inplace=True, ascending=False)
        meta_data = {'6. Time Zone': US_EASTERN}
        return frame, meta_data

    @staticmethod
    def get_intraday_csv(symbol: str):
        intraday_list = [('time', 'open', 'high', 'low', 'close', 'volume')]
        decimal_list = full((10,), Decimal(500))
        dates = date_range(end='2020-02-02', periods=10).to_pydatetime().tolist()
        for date, decimal in zip(dates, decimal_list):
            intraday_list.append((date, decimal, decimal, decimal, decimal, decimal, symbol))
        return intraday_list, None

    @staticmethod
    def truncate_tables():
        PortfolioEntity.query.delete()
        EvaluationEntity.query.delete()
        IntradayEntity.query.delete()
        ForwardEntity.query.delete()
        StockEntity.query.delete()
        ConfigurationEntity.query.delete()

    @staticmethod
    def create_datetime(date: Union[str, datetime], tz: str = US_EASTERN):
        if isinstance(date, str):
            return timezone(tz).localize(datetime.fromisoformat(date))
        elif isinstance(date, datetime):
            return timezone(tz).localize(date)
        else:
            raise AttributeError

    @classmethod
    def create_default_intraday_list(cls):
        aaa = full(150, Decimal(500))
        bbb = copy.copy(aaa)
        ccc = copy.copy(aaa)
        aaa[30:60] = aaa[90:120] = ccc[0:30] = ccc[60:90] = ccc[120:150] = Decimal(100)
        bbb[0:30] = NAN
        prices_aaa = cls.create_intraday_list(decimal_list=aaa, symbol='AAA')
        prices_bbb = cls.create_intraday_list(decimal_list=bbb, symbol='BBB')
        prices_ccc = cls.create_intraday_list(decimal_list=ccc, symbol='CCC')
        return prices_aaa + prices_bbb + prices_ccc

    @staticmethod
    def create_intraday_list(symbol_list=None, decimal_list=None, size=10, symbol='AAA'):
        if symbol_list is not None:
            size = len(symbol_list)
        if decimal_list is not None:
            size = len(decimal_list)
        intraday_list = []
        if symbol_list is None:
            symbol_list = [symbol for _ in range(size)]
        if decimal_list is None:
            decimal_list = [Decimal(i) for i in range(size)]
        dates = date_range(end='2020-02-02', periods=size).to_pydatetime().tolist()
        for date, symbol, decimal in zip(dates, symbol_list, decimal_list):
            intraday = IntradayEntity()
            Utils.set_attributes(intraday, date=date, open=decimal, high=decimal, low=decimal, close=decimal,
                                 volume=decimal, symbol=symbol)
            intraday_list.append(intraday)
        return intraday_list
