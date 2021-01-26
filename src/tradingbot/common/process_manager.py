import multiprocessing
from multiprocessing.context import Process
from typing import Dict, List, Tuple, Any, Optional, Final

from tradingbot.bo.forward_bo import ForwardBO
from tradingbot.bo.intraday_bo import IntradayBO
from tradingbot.bo.optimization_bo import OptimizationBO
from tradingbot.bo.portfolio_bo import PortfolioBO
from tradingbot.common.database import Database
from tradingbot.common.scheduler import Scheduler
from tradingbot.dao.stock_dao import StockDAO


class ProcessManager:
    TARGET: Final[str] = 'target'
    ARGS: Final[str] = 'args'

    CONFIGURATION: Dict[str, Dict[str, Tuple[Any, ...]]] = {
        'init-database': {
            TARGET: Database.init,
            ARGS: []
        },
        'update-table-stock': {
            TARGET: StockDAO.update,
            ARGS: (PortfolioBO.backward_forward_portfolio(),)
        },
        'update-table-intraday': {
            TARGET: IntradayBO.update,
            ARGS: (PortfolioBO.backward_forward_portfolio(),)
        },
        'schedule': {
            TARGET: Scheduler.start,
            ARGS: []
        },
        'optimize': {
            TARGET: OptimizationBO.start,
            ARGS: (PortfolioBO.backward_portfolio(), 100, 4)
        },
        'forward': {
            TARGET: ForwardBO.start,
            ARGS: (PortfolioBO.forward_portfolio(),)
        }
    }

    @classmethod
    def start(cls, name: str) -> bool:
        if name in cls.CONFIGURATION.keys():
            configuration: Dict[str, Tuple[Any, ...]] = cls.CONFIGURATION.get(name)
            process: Process = cls.__find(name)
            if process is None or not process.is_alive():
                process = multiprocessing.Process(name=name, target=configuration.get(cls.TARGET),
                                                  args=configuration.get(cls.ARGS))
                process.start()
                return True
        return False

    @classmethod
    def stop(cls, name: str) -> bool:
        if name in cls.CONFIGURATION.keys():
            process: Process = cls.__find(name)
            if process is not None:
                process.terminate()
                process.join()
                return True
        return False

    @staticmethod
    def running() -> bool:
        return len(multiprocessing.active_children()) > 0

    @staticmethod
    def get_active_names() -> List[str]:
        return sorted(list(map(lambda p: p.name, list(multiprocessing.active_children()))))

    @classmethod
    def get_inactive_names(cls) -> List[str]:
        return sorted(list(filter(lambda p: p not in cls.get_active_names(), cls.CONFIGURATION.keys())))

    @staticmethod
    def __find(name: str) -> Optional[Process]:
        return next(iter(filter(lambda p: p.name == name, multiprocessing.active_children())), None)
