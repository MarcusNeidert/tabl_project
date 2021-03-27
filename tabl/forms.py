from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, SelectField, widgets
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from tabl.models import User, Cookware, Ingredient
from tabl import db

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    def pre_validate(self, form):
        pass

class RegistrationForm(FlaskForm):
    username = StringField('Chef name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    user_style              = SelectField('Choose your favourite style of cooking', choices=[], coerce=int)
    user_cookware           = MultiCheckboxField('What cookware do you have at your disposal', choices=[], coerce=int,
                                                 validators=[DataRequired()])
    carbs_intolerances      = MultiCheckboxField('Carbohydrates', choices=[], coerce=int)
    protein_intolerances    = MultiCheckboxField('Proteins', choices=[], coerce=int)
    flavouring_intolerances = MultiCheckboxField('Flavourings', choices=[], coerce=int)
    submit = SubmitField('Get cookin\u0027')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email    = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email    = StringField('Email',
                        validators=[DataRequired(), Email()])
    update_style                   = SelectField('Favourite style', choices=[], coerce=int)
    update_cookware                = MultiCheckboxField('Your Cookware', choices=[], coerce=int)
    update_carbs_intolerances      = MultiCheckboxField('Carbohydrates', choices=[], coerce=int)
    update_protein_intolerances    = MultiCheckboxField('Proteins', choices=[], coerce=int)
    update_flavouring_intolerances = MultiCheckboxField('Flavourings', choices=[], coerce=int)
    picture         = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit          = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class EditStyleForm(FlaskForm):
    new_style = StringField('Add style',
                            validators=[Optional(), Length(min=2, max=20)])
    remove_styles = MultiCheckboxField('Remove styles', choices=[], coerce=int)
    submit = SubmitField('Add | Remove')

class EditCookwareForm(FlaskForm):
    new_cookware = StringField('Add cookware',
                           validators=[Optional(), Length(min=2, max=20)])
    remove_cookware = MultiCheckboxField('Remove cookware', choices=[], coerce=int)
    submit = SubmitField('Add | Remove')

class EditIngredientForm(FlaskForm):
    new_ingredient_name     = StringField('Add ingredient',
                           validators=[Optional(), Length(min=2, max=20)])
    new_ingredient_category = SelectField('Category', choices=[],
                                          validators=[DataRequired()])
    remove_carbs         = MultiCheckboxField('Carbohydrates', choices=[], coerce=int)
    remove_proteins      = MultiCheckboxField('Proteins', choices=[], coerce=int)
    remove_flavourings   = MultiCheckboxField('Flavourings', choices=[], coerce=int)
    submit = SubmitField('Add | Remove')