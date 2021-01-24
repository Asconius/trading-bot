from datetime import datetime
from decimal import Decimal
from typing import List, NoReturn

from sqlalchemy import func

from src import db
from src.dao.base_dao import BaseDAO
from src.entity.forward_entity import ForwardEntity
from src.enums.action_enum import ActionEnum
from src.enums.strategy_enum import StrategyEnum
from src.utils.utils import Utils


class ForwardDAO(BaseDAO):

    @classmethod
    def create_buy(cls, symbol: str, price: Decimal, number: Decimal, cash: Decimal,
                   strategy: StrategyEnum) -> NoReturn:
        forward: ForwardEntity = cls.__init(ActionEnum.BUY, symbol, price, number, cash, strategy)
        cls.persist(forward)

    @classmethod
    def create_sell(cls, symbol: str, price: Decimal, number: Decimal, cash: Decimal,
                    strategy: StrategyEnum) -> NoReturn:
        forward: ForwardEntity = cls.__init(ActionEnum.SELL, symbol, price, number, cash, strategy)
        cls.persist(forward)

    @staticmethod
    def read_all() -> List[ForwardEntity]:
        return ForwardEntity.query.all()

    @staticmethod
    def read_filter_by_strategy_and_max_timestamp(strategy: StrategyEnum) -> datetime:
        return Utils.first(db.session.query(func.max(ForwardEntity.timestamp)).filter_by(strategy=strategy).first())

    @staticmethod
    def read_filter_by_strategy(strategy: StrategyEnum) -> List[ForwardEntity]:
        return ForwardEntity.query.filter_by(strategy=strategy).order_by(ForwardEntity.timestamp.asc()).all()

    @staticmethod
    def __init(action: ActionEnum, symbol: str, price: Decimal, number: Decimal, cash: Decimal,
               strategy: StrategyEnum) -> ForwardEntity:
        forward: ForwardEntity = ForwardEntity()
        Utils.set_attributes(forward, timestamp=Utils.now(), symbol=symbol, action=action, price=price, number=number,
                             cash=cash, strategy=strategy)
        return forward
