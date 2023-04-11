from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class PasswordForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    site_url = StringField("URL сайта")
    # is_private = BooleanField("Личное")
    site_password = PasswordField("Пароль")
    submit = SubmitField('Применить')