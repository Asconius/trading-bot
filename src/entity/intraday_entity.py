from sqlalchemy_utc import UtcDateTime

from src import db
from src.entity.stock_entity import StockEntity


class IntradayEntity(db.Model):
    __tablename__ = 'intraday'
    date = db.Column(UtcDateTime, nullable=False, primary_key=True)
    open = db.Column(db.DECIMAL)
    high = db.Column(db.DECIMAL)
    low = db.Column(db.DECIMAL)
    close = db.Column(db.DECIMAL)
    volume = db.Column(db.DECIMAL)
    symbol = db.Column(db.String(10), db.ForeignKey(StockEntity.symbol), nullable=False, index=True, primary_key=True)
