from tradingbot import db


class ConfigurationEntity(db.Model):
    __tablename__ = 'configuration'
    identifier = db.Column(db.String(10), nullable=False, index=True, primary_key=True)
    value = db.Column(db.DECIMAL)
    description = db.Column(db.Text)
