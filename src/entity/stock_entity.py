from src import db


class StockEntity(db.Model):
    __tablename__ = 'stock'
    ticker = db.Column(db.String(10), nullable=False, index=True, primary_key=True)
    isin = db.Column(db.String(20))
