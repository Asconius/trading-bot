import math
from datetime import datetime
from decimal import Decimal
from typing import Tuple, List

from pandas import DataFrame

from src.common.constants import ZERO
from src.converter.intraday_entity_converter import IntradayEntityConverter
from src.dto.attempt_dto import AttemptDTO
from src.entity.intraday_entity import IntradayEntity
from src.enums.action_enum import ActionEnum
from src.utils.utils import Utils


class StrategyBO:
    # noinspection DuplicatedCode
    @staticmethod
    def counter_cyclical(intraday_list: List[IntradayEntity], date: datetime,
                         attempt: AttemptDTO) -> Tuple[ActionEnum, Decimal]:
        frame: DataFrame = IntradayEntityConverter.to_dataframe(intraday_list)
        normalized: DataFrame = Utils.normalize(frame)
        close: Decimal = frame.at[date, normalized.columns[0]]
        end_close: Decimal = normalized.at[date, normalized.columns[0]]
        if attempt is None:
            attempt = AttemptDTO()
        start_close: Decimal = Utils.day_delta_value(normalized, date, attempt.distance_buy)
        if not math.isnan(start_close):
            percent: Decimal = start_close - end_close
            if not math.isnan(start_close) and not math.isnan(end_close) and percent > attempt.delta_buy:
                return ActionEnum.BUY, Utils.number(attempt.amount_buy, close)
        start_close: Decimal = Utils.day_delta_value(normalized, date, attempt.distance_sell)
        if not math.isnan(start_close):
            percent: Decimal = end_close - start_close
            if not math.isnan(start_close) and not math.isnan(end_close) and percent > attempt.delta_sell:
                return ActionEnum.SELL, Utils.number(attempt.amount_sell, close)
        return ActionEnum.NONE, ZERO

    # noinspection DuplicatedCode
    @staticmethod
    def volume_trading(intraday_list: List[IntradayEntity], date: datetime,
                       attempt: AttemptDTO) -> Tuple[ActionEnum, Decimal]:
        frame: DataFrame = IntradayEntityConverter.to_dataframe(intraday_list, column='volume')
        normalized: DataFrame = Utils.normalize(frame)
        volume: Decimal = frame.at[date, normalized.columns[0]]
        end_volume: Decimal = normalized.at[date, normalized.columns[0]]
        if attempt is None:
            attempt = AttemptDTO()
        start_volume: Decimal = Utils.day_delta_value(normalized, date, attempt.distance_buy)
        if not math.isnan(start_volume):
            percent: Decimal = start_volume - end_volume
            if not math.isnan(start_volume) and not math.isnan(end_volume) and percent > attempt.delta_buy:
                return ActionEnum.BUY, Utils.number(attempt.amount_buy, volume)
        start_volume: Decimal = Utils.day_delta_value(normalized, date, attempt.distance_sell)
        if not math.isnan(start_volume):
            percent: Decimal = end_volume - start_volume
            if not math.isnan(start_volume) and not math.isnan(end_volume) and percent > attempt.delta_sell:
                return ActionEnum.SELL, Utils.number(attempt.amount_sell, volume)
        return ActionEnum.NONE, ZERO
