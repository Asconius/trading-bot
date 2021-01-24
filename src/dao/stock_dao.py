from typing import Tuple, List, Union, NoReturn

from src.bo.stock_bo import StockBO
from src.dao.base_dao import BaseDAO
from src.entity.stock_entity import StockEntity
from src.utils.utils import Utils


class StockDAO(BaseDAO):

    @classmethod
    def create_if_not_exists(cls, portfolio: Tuple[str]) -> NoReturn:
        rows: List[StockEntity] = StockEntity.query.with_entities(StockEntity.symbol).filter(
            StockEntity.symbol.in_(portfolio)).all()
        if len(rows) < len(portfolio):
            cls.update(portfolio)

    @staticmethod
    def read_all() -> List[StockEntity]:
        return StockEntity.query.all()

    @staticmethod
    def read_symbol() -> List[StockEntity]:
        return StockEntity.query.with_entities(StockEntity.symbol).all()

    @classmethod
    def update(cls, portfolio: Tuple[Union[str, None], ...]) -> NoReturn:
        for symbol in portfolio:
            stock: StockEntity = StockEntity()
            Utils.set_attributes(stock, symbol=symbol, isin=StockBO.isin(symbol))
            cls.persist(stock)
