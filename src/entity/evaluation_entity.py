from sqlalchemy_utc import UtcDateTime

from src import db
from src.enums.strategy_enum import StrategyEnum


class EvaluationEntity(db.Model):
    __tablename__ = 'evaluation'
    timestamp = db.Column(UtcDateTime, nullable=False, primary_key=True)
    sum = db.Column(db.DECIMAL, index=True)
    funds = db.Column(db.Text)
    amount_buy = db.Column(db.DECIMAL)
    distance_buy = db.Column(db.DECIMAL)
    delta_buy = db.Column(db.DECIMAL)
    amount_sell = db.Column(db.DECIMAL)
    distance_sell = db.Column(db.DECIMAL)
    delta_sell = db.Column(db.DECIMAL)
    strategy = db.Column(db.Enum(StrategyEnum))
