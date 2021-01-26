from tradingbot import db
from tradingbot.bo.configuration_bo import ConfigurationBO
from tradingbot.bo.portfolio_bo import PortfolioBO


class Database:

    @staticmethod
    def init() -> None:
        db.create_all()
        ConfigurationBO.init()
        PortfolioBO.init()
