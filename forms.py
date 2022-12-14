from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import current_user
import main


class CreateProductForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])


class CreateUserOrderForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    product = QuerySelectField(
        query_factory=main.Product.query.all, allow_blank=False, get_label='name', get_pk=lambda obj: str(obj)
    )


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password1', message='Passwords do not match!')]
    )

    def validate_username(self, username):
        user = main.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User name already exists!')


class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class UpdateUserAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])

    def validate_username(self, username):
        if username.data != current_user.username:
            user = main.User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('User name already exists!')
