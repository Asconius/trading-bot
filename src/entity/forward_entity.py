from sqlalchemy_utc import UtcDateTime

from src import db
from src.entity.stock_entity import StockEntity
from src.enums.action_enum import ActionEnum
from src.enums.strategy_enum import StrategyEnum


class ForwardEntity(db.Model):
    __tablename__ = 'forward'
    timestamp = db.Column(UtcDateTime, nullable=False, index=True, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey(StockEntity.symbol), nullable=False, primary_key=True)
    action = db.Column(db.Enum(ActionEnum))
    price = db.Column(db.DECIMAL)
    number = db.Column(db.DECIMAL)
    cash = db.Column(db.DECIMAL)
    strategy = db.Column(db.Enum(StrategyEnum))
