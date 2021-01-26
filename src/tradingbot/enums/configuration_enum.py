from decimal import Decimal
from enum import Enum


class ConfigurationEnum(Enum):
    FORWARD_CASH = ('FORWARD_CASH', Decimal('10000'), 'Forward Cash')
    FORWARD_FEE = ('FORWARD_FEE', Decimal('3.9'), 'Forward Fee')
    OPTIMIZATION_CASH = ('OPTIMIZATION_CASH', Decimal('10000'), 'Optimization Cash')
    OPTIMIZATION_FEE = ('OPTIMIZATION_FEE', Decimal('3.9'), 'Optimization Fee')

    def __init__(self, identifier: str, value: Decimal, description: str):
        self.identifier = identifier
        self.val = value
        self.description = description
