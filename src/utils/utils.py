import os
import random
import sys
from datetime import timedelta, datetime
from decimal import Decimal, ROUND_DOWN, ExtendedContext
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Iterable, List, Iterator, Tuple, Optional, TypeVar, Sequence, NoReturn, Union

import pandas as pd
import pytz
from numpy import ndarray
from pandas import DataFrame
from workalendar.usa import NewYork

from src.common.constants import US_EASTERN, ZERO, NAN

T = TypeVar('T')


class Utils:

    @staticmethod
    def valid(start: Decimal, value: Decimal, stop: Decimal) -> bool:
        return start <= value <= stop

    @staticmethod
    def negation() -> Decimal:
        return Decimal('1') if random.random() < 0.5 else Decimal('-1')

    @staticmethod
    def inverse() -> Decimal:
        return Decimal(random.random()) if random.random() < 0.5 else Decimal(1 / (1 - random.random()))

    @staticmethod
    def group(number: int, iterable: List[T]) -> Tuple[Tuple[T]]:
        args: Iterable[Iterator] = [iter(iterable)] * number
        return tuple(zip(*args))

    @staticmethod
    def number(numerator: Decimal, denominator: Decimal) -> Decimal:
        return ZERO if denominator == ZERO else ExtendedContext.divide_int(numerator, denominator)

    @staticmethod
    def divide(numerator: Union[Decimal, ndarray], denominator: Union[Decimal, ndarray]) -> Union[Decimal, ndarray]:
        return ZERO if denominator == ZERO else numerator / denominator

    @staticmethod
    def day_delta_value(frame: DataFrame, date: datetime, delta: Decimal) -> Decimal:
        column: str = frame.columns[0]
        interval_end = date - timedelta(days=float(delta))
        interval_start = date - timedelta(days=float(delta) + 7)
        interval_date = frame.loc[interval_start:interval_end, column].index.max()
        if pd.isnull(interval_date):
            return NAN
        return frame.at[interval_date, column]

    @classmethod
    def is_today(cls, today: Optional[datetime]) -> bool:
        return False if not isinstance(today, datetime) else cls.now().date() == today.date()

    @staticmethod
    def now() -> datetime:
        return pytz.utc.localize(datetime.utcnow())

    @classmethod
    def is_working_day_ny(cls) -> datetime:
        return NewYork().is_working_day(cls.now().astimezone(pytz.timezone(US_EASTERN)))

    @staticmethod
    def first(sequence: Sequence[T]) -> Optional[T]:
        return None if len(sequence) == 0 else sequence[0]

    @staticmethod
    def set_attributes(assignable: object, **kwargs: any) -> NoReturn:
        for key, value in kwargs.items():
            setattr(assignable, key, value)

    @staticmethod
    def truncate(number: Decimal) -> Decimal:
        return Decimal(number).quantize(Decimal('1'), rounding=ROUND_DOWN)

    @staticmethod
    def is_test() -> bool:
        return len(sys.argv) > 0 and 'test' in sys.argv[0]

    @staticmethod
    def send_mail(text: str):
        from_address: str = os.getenv('FROM_EMAIL_ADDRESS')
        to_address: str = os.getenv('TO_EMAIL_ADDRESS')
        password: str = os.getenv('EMAIL_PASSWORD')
        msg: MIMEText = MIMEText(text)
        msg['Subject'] = 'trading-bot'
        msg['From'] = from_address
        msg['To'] = to_address
        smtp: SMTP = SMTP(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT'))
        smtp.starttls()
        smtp.login(from_address, password)
        smtp.sendmail(from_address, to_address, msg.as_string())

    @classmethod
    def normalize(cls, frame: DataFrame) -> DataFrame:
        data: ndarray = frame.values
        data_mean: ndarray = data.mean(axis=0)
        data_std: ndarray = data.std(axis=0)
        features: ndarray = cls.divide(data - data_mean, data_std)
        return DataFrame(features, index=frame.index, columns=frame.columns)


if __name__ == '__main__':
    Utils.send_mail('This is the body of the message.')
