from __future__ import annotations

from typing import Optional

from flask import request
from wtforms import Form, FieldList, FormField, SubmitField

from tradingbot.enums.mode_enum import ModeEnum
from tradingbot.form.portfolio_field_form import PortfolioFieldForm


class PortfolioForm(Form):
    form_list = FieldList(FormField(PortfolioFieldForm))
    submit = SubmitField('Submit')

    @staticmethod
    def append_form(isin: str, symbol: str, mode: Optional[ModeEnum], form: PortfolioForm) -> None:
        field_form: PortfolioFieldForm = PortfolioFieldForm(request.form)
        field_form.isin = isin
        field_form.symbol = symbol
        field_form.mode = mode
        form.form_list.append_entry(field_form)
