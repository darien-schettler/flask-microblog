from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


# To handle the web forms in this application I'm going to use the Flask-WTF extension, which is a thin wrapper
# around the WTForms package that nicely integrates it with Flask
#
# The Flask-WTF extension uses Python classes to represent web forms. A form class simply defines the fields of the
# form as class variables.
#
# Once again having separation of concerns in mind, I'm going to use a new app/forms.py module to store my web form
# classes.

class LoginForm(FlaskForm):
    # The 4 classes that represent the field types that I'm using for this form are imported directly from the
    # WTForms package, since the Flask-WTF extension does not provide customized versions. For each field,
    # an object is created as a class variable in the LoginForm class. Each field is given a description or label as
    # a first argument. The optional validators argument that you see in some of the fields is used to attach
    # validation behaviors to fields. The DataRequired validator simply checks that the field is not submitted empty.
    # There are many more validators available, some of which will be used in other forms.
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])  # Force Check
    submit = SubmitField('Register')

    # FNs with the validate_#%@% syntax are passed as additional validation requirements
    # This validation is to ensure that the passed username isn't already in the database
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # This validation is to ensure that the passed email isn't already in the database
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Form to allow for the request to reset a users password
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


# Form to allow for the user to enter a new password when in the process of resetting their password
class ResetPasswordForm(FlaskForm):

    # Double validation to ensure correct/meaningful entry of password data
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Request Password Reset')
