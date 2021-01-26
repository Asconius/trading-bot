import logging

from sqlalchemy.exc import SQLAlchemyError

from tradingbot import db


class BaseDAO:

    @classmethod
    def persist(cls, entity: db.Model) -> None:
        db.session.add(entity)
        cls.commit()

    @staticmethod
    def commit() -> None:
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()
