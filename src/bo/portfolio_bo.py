import hashlib
from typing import List, Any, NoReturn, Tuple, Union, Final

from yahoo_fin.stock_info import tickers_sp500, tickers_nasdaq

from src.dao.portfolio_dao import PortfolioDAO
from src.dao.stock_dao import StockDAO
from src.entity.portfolio_entity import PortfolioEntity
from src.enums.mode_enum import ModeEnum


class PortfolioBO:
    PORTFOLIO_SIZE: Final[int] = 100

    @classmethod
    def backward_portfolio(cls, size: int = PORTFOLIO_SIZE) -> List[str]:
        return cls.__sort(PortfolioDAO.read_filter_by_mode(ModeEnum.BACKWARD)[:size])

    @classmethod
    def forward_portfolio(cls, size: int = PORTFOLIO_SIZE) -> List[str]:
        return cls.__sort(PortfolioDAO.read_filter_by_mode(ModeEnum.FORWARD)[:size])

    @classmethod
    def backward_forward_portfolio(cls, size: int = PORTFOLIO_SIZE) -> List[str]:
        return cls.forward_portfolio(size) + cls.backward_portfolio(size)

    @staticmethod
    def __sort(portfolio: List[PortfolioEntity]) -> List[str]:
        return sorted(list(map(lambda p: p.symbol, portfolio)), key=lambda x: hashlib.md5(x.encode()).hexdigest())

    @classmethod
    def init(cls) -> NoReturn:
        symbol_list: Tuple[Union[str, None], ...] = tickers_sp500() + tickers_nasdaq()
        StockDAO.update(symbol_list)
        for symbol in symbol_list:
            PortfolioDAO.create(symbol, ModeEnum.BACKWARD)
            PortfolioDAO.create(symbol, ModeEnum.FORWARD)

    @staticmethod
    def read() -> List[Any]:
        return PortfolioDAO.read()

    @staticmethod
    def read_filter_by_symbol_isin(symbol: str) -> Any:
        return PortfolioDAO.read_filter_by_symbol_isin(symbol)

    @staticmethod
    def update(symbol: str, mode: ModeEnum) -> NoReturn:
        StockDAO.create_if_not_exists((symbol,))
        PortfolioDAO.update(symbol, mode)

    @staticmethod
    def delete(symbol: str) -> NoReturn:
        PortfolioDAO.delete(symbol)
