import multiprocessing
import time
from unittest.mock import patch

from tests.base_test_case import BaseTestCase
from tradingbot.bo.forward_bo import ForwardBO
from tradingbot.bo.intraday_bo import IntradayBO
from tradingbot.bo.optimization_bo import OptimizationBO
from tradingbot.bo.portfolio_bo import PortfolioBO
from tradingbot.common.constants import EMPTY
from tradingbot.common.process_manager import ProcessManager
from tradingbot.common.scheduler import Scheduler
from tradingbot.dao.stock_dao import StockDAO


class ProcessManagerTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.truncate_tables()

    class TestProcess:
        @staticmethod
        def test():
            time.sleep(1)

    CONFIGURATION = {
        'test1': {
            ProcessManager.TARGET: TestProcess.test,
            ProcessManager.ARGS: []
        },
        'test2': {
            ProcessManager.TARGET: TestProcess.test,
            ProcessManager.ARGS: []
        }
    }

    def test_configuration(self):
        names = ['init-database', 'update-table-stock', 'update-table-intraday', 'schedule', 'optimize', 'forward']
        self.assertListEqual(list(ProcessManager.CONFIGURATION.keys()), names)
        update_table_stock = ProcessManager.CONFIGURATION['update-table-stock']
        self.assertEqual(update_table_stock[ProcessManager.TARGET], StockDAO.update)
        self.assertEqual(update_table_stock[ProcessManager.ARGS], (PortfolioBO.backward_forward_portfolio(),))
        update_table_intraday = ProcessManager.CONFIGURATION['update-table-intraday']
        self.assertEqual(update_table_intraday[ProcessManager.TARGET], IntradayBO.update)
        self.assertEqual(update_table_intraday[ProcessManager.ARGS], (PortfolioBO.backward_forward_portfolio(),))
        schedule = ProcessManager.CONFIGURATION['schedule']
        self.assertEqual(schedule[ProcessManager.TARGET], Scheduler.start)
        self.assertEqual(schedule[ProcessManager.ARGS], [])
        optimize = ProcessManager.CONFIGURATION['optimize']
        self.assertEqual(optimize[ProcessManager.TARGET], OptimizationBO.start)
        self.assertEqual(optimize[ProcessManager.ARGS], (PortfolioBO.backward_portfolio(), 100, 4))
        forward = ProcessManager.CONFIGURATION['forward']
        self.assertEqual(forward[ProcessManager.TARGET], ForwardBO.start)
        self.assertEqual(forward[ProcessManager.ARGS], (PortfolioBO.forward_portfolio(),))

    @patch('tradingbot.common.process_manager.ProcessManager.CONFIGURATION', new=CONFIGURATION)
    def test_successful(self):
        self.__start('test1', True, True, ['test1'], ['test2'])
        self.__start('test1', False, True, ['test1'], ['test2'])
        self.__stop('test1', True, False, [], ['test1', 'test2'])

    @patch('tradingbot.common.process_manager.ProcessManager.CONFIGURATION', new=CONFIGURATION)
    def test_successful_twice(self):
        self.__stop('test1', False, False, [], ['test1', 'test2'])
        self.__start('test1', True, True, ['test1'], ['test2'])
        self.__stop('test1', True, False, [], ['test1', 'test2'])
        self.__start('test1', True, True, ['test1'], ['test2'])
        self.__stop('test1', True, False, [], ['test1', 'test2'])

    @patch('tradingbot.common.process_manager.ProcessManager.CONFIGURATION', new=CONFIGURATION)
    def test_successful_with_second(self):
        self.__start('test1', True, True, ['test1'], ['test2'])
        self.__start('test2', True, True, ['test1', 'test2'], [])
        self.__stop('test2', True, True, ['test1'], ['test2'])
        self.__stop('test1', True, False, [], ['test1', 'test2'])

    @patch('tradingbot.common.process_manager.ProcessManager.CONFIGURATION', new=CONFIGURATION)
    def test_successful_wait(self):
        self.__start('test1', True, True, ['test1'], ['test2'])
        while len(multiprocessing.active_children()) > 0:
            pass  # Do nothing
        self.assertEqual(ProcessManager.running(), False)
        self.assertListEqual(ProcessManager.get_active_names(), [])
        self.assertListEqual(ProcessManager.get_inactive_names(), ['test1', 'test2'])
        self.__start('test1', True, True, ['test1'], ['test2'])
        self.__stop('test1', True, False, [], ['test1', 'test2'])

    @patch('tradingbot.common.process_manager.ProcessManager.CONFIGURATION', new=CONFIGURATION)
    def test_failed(self):
        self.__start(EMPTY, False, False, [], ['test1', 'test2'])
        self.__stop(EMPTY, False, False, [], ['test1', 'test2'])

    def __start(self, name, successful, running, active_names, inactive_names):
        self.assertEqual(ProcessManager.start(name), successful)
        time.sleep(0.1)
        self.assertEqual(ProcessManager.running(), running)
        self.assertListEqual(ProcessManager.get_active_names(), active_names)
        self.assertListEqual(ProcessManager.get_inactive_names(), inactive_names)

    def __stop(self, name, successful, running, active_names, inactive_names):
        self.assertEqual(ProcessManager.stop(name), successful)
        time.sleep(0.1)
        self.assertEqual(ProcessManager.running(), running)
        self.assertListEqual(ProcessManager.get_active_names(), active_names)
        self.assertListEqual(ProcessManager.get_inactive_names(), inactive_names)
