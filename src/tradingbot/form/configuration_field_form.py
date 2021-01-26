from wtforms import Form, StringField, HiddenField, DecimalField
from wtforms.validators import DataRequired, NumberRange


class ConfigurationFieldForm(Form):
    identifier: HiddenField = HiddenField('Identifier')
    value: DecimalField = DecimalField('Value', validators=[DataRequired(), NumberRange(
        min=0, max=1000000, message='The value must be between 0 and 1000000')])
    description: StringField = StringField('Description', render_kw={'readonly': True})
