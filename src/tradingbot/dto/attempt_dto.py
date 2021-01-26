from __future__ import annotations

from decimal import Decimal


class AttemptDTO:

    def __init__(self, amount_buy: Decimal = Decimal('1000'), distance_buy: Decimal = Decimal('30'),
                 delta_buy: Decimal = Decimal('1.5'), amount_sell: Decimal = Decimal('1000'),
                 distance_sell: Decimal = Decimal('30'), delta_sell: Decimal = Decimal('1.5')) -> None:
        self.amount_buy: Decimal = amount_buy
        self.distance_buy: Decimal = distance_buy
        self.delta_buy: Decimal = delta_buy
        self.amount_sell: Decimal = amount_sell
        self.distance_sell: Decimal = distance_sell
        self.delta_sell: Decimal = delta_sell
