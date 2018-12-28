# Mapped classes for the HTML forms generated by WTForms

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


class CrawlingRuleForm(FlaskForm):
    address = StringField('Web page address', validators=[DataRequired(), URL()])
    selector = StringField('CSS selector', validators=[DataRequired()])
    submit = SubmitField('Add crawling rule')
