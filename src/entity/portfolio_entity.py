from src import db
from src.entity.stock_entity import StockEntity
from src.enums.mode_enum import ModeEnum


class PortfolioEntity(db.Model):
    __tablename__ = 'portfolio'
    symbol = db.Column(db.String(10), db.ForeignKey(StockEntity.symbol), nullable=False, index=True, primary_key=True)
    mode = db.Column(db.Enum(ModeEnum), primary_key=True)
