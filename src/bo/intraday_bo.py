from datetime import datetime
from time import sleep
from typing import List, Tuple, NoReturn

from src import db
from src.common.constants import REQUEST_SLEEP
from src.dao.intraday_dao import IntradayDAO
from src.dao.stock_dao import StockDAO
from src.entity.intraday_entity import IntradayEntity
from src.utils.utils import Utils


class IntradayBO:

    @staticmethod
    def sort_by_date(intraday_list: List[IntradayEntity]):
        return sorted(intraday_list, key=lambda i: i.date)

    @staticmethod
    def group_by_symbol(intraday_list: List[IntradayEntity]):
        return {b: [a for a in intraday_list if a.symbol == b] for b in set(map(lambda b: b.symbol, intraday_list))}

    @staticmethod
    def update(portfolio: Tuple[str, ...]) -> NoReturn:
        StockDAO.create_if_not_exists(portfolio)
        rows: List[IntradayEntity] = IntradayEntity.query.with_entities(IntradayEntity.symbol).filter(
            IntradayEntity.symbol.in_(portfolio)).distinct(IntradayEntity.symbol).all()
        if len(rows) < len(portfolio):
            symbols: List[str] = list(map(lambda r: r.symbol, rows))
            difference: str = Utils.first(sorted(list(set(portfolio) - set(symbols))))
            if difference is not None:
                IntradayDAO.create_symbol_extended(difference)
        else:
            for _ in range(24):
                rows: List[IntradayEntity] = db.session.query(IntradayEntity.symbol, db.func.max(
                    IntradayEntity.date)).group_by(IntradayEntity.symbol).all()
                if rows is not None:
                    latest_date: datetime = max(list(map(lambda r: r[1], rows))).date()
                    symbol: str = Utils.first(sorted(list(map(
                        lambda r: r.symbol, list(filter(lambda f, d=latest_date: (f[1].date() != d), rows))))))
                    if symbol is not None:
                        IntradayDAO.create_symbol(symbol)
                if not Utils.is_test():
                    sleep(REQUEST_SLEEP)
