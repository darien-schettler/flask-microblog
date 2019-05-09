from app.email import send_email
from flask import render_template, current_app


# The send_password_reset_email() FN is used to generate the password reset emails
# The send_password_reset_email() FN relies on the send_email() function I wrote above
# The interesting part in this function is that the text and HTML content for the emails is generated from templates
# using the familiar render_template() function. The templates receive the user and the token as arguments,
# so that a personalized email message can be generated.
def send_password_reset_email(user):
    # Get the token by utilizing the get_reset_password_token method from the user model
    token = user.get_reset_password_token()

    # Use the above function to compose and send an email using render template and users email address and token
    send_email("[Acorn's Microblog] Reset Your Password",
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',    user=user, token=token),
               html_body=render_template('email/reset_password.html',   user=user, token=token))
