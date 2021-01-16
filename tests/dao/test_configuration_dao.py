from decimal import Decimal

from src import db
from src.bo.configuration_bo import ConfigurationBO
from src.dao.configuration_dao import ConfigurationDAO
from src.entity.configuration_entity import ConfigurationEntity
from src.enums.configuration_enum import ConfigurationEnum
from tests.base_test_case import BaseTestCase


class ConfigurationDAOTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        self.truncate_tables()
        ConfigurationBO.init()

    def test_read_filter_by_identifier(self):
        configuration = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.FORWARD_CASH.identifier)
        self.assertIsInstance(configuration, ConfigurationEntity)
        self.assert_attributes(configuration, identifier=ConfigurationEnum.FORWARD_CASH.identifier,
                               value=ConfigurationEnum.FORWARD_CASH.val,
                               description=ConfigurationEnum.FORWARD_CASH.description)

    def test_update(self):
        ConfigurationDAO.update(ConfigurationEnum.FORWARD_CASH.identifier, Decimal('10001'))
        configuration = ConfigurationDAO.read_filter_by_identifier(ConfigurationEnum.FORWARD_CASH.identifier)
        self.assertIsInstance(configuration, ConfigurationEntity)
        self.assert_attributes(configuration, identifier=ConfigurationEnum.FORWARD_CASH.identifier,
                               value=10001, description=ConfigurationEnum.FORWARD_CASH.description)
