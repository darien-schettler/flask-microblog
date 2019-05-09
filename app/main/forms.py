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


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    # GET MICHAEL'S HELP ON THIS
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


# Form to allow for the creation of block posts
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
