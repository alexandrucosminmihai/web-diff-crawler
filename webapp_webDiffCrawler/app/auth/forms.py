from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from webDiffCrawler.webDiffCrawler.mappedClasses import Users
from webapp_webDiffCrawler.app import dbSession


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          'Usernames must have only letters, numbers, dots or '
                                                          'underscores')])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    secrettoken = StringField('Secret token', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if dbSession.query(Users).filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if dbSession.query(Users).filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_secrettoken(self, field):
        user = dbSession.query(Users).filter_by(secrettoken=field.data).first()
        # If the token does not exist or has already been used
        if (not user) or user.email or user.username or user.password_hash:
            raise ValidationError('Invalid secret token.')


class SecretTokenGenrationForm(FlaskForm):
    isAdmin = BooleanField('Make admin')
    submit = SubmitField('New secret token')