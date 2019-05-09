from flask_mail import Message
from app import mail, app
from flask import render_template


# ----------------------------------------- Helper FN that sends an email -------------------------------------------
#   NOTE: Flask-Mail supports some features that I'm not utilizing here such as Cc and Bcc lists. (SEE FLASK-MAIL DOCS)
#   ARGS:
#        - subject       :  Subject Line of The Email
#        - sender        :  Sender Email Address
#        - recipients    :  Recipient Email Address(es)
#        - text_body     :  Non-HTML Version of the Email
#        - html_body     :  HTML Version of the Email (This version should render whenever possible as it's prettier)
#   Message FN:
#        - configures the email parameters and has fields respective to the passed arguments
# -------------------------------------------------------------------------------------------------------------------
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
# -------------------------------------------------------------------------------------------------------------------


# The send_password_reset_email() FN is used to generate the password reset emails
# The send_password_reset_email() FN relies on the send_email() function I wrote above
# The interesting part in this function is that the text and HTML content for the emails is generated from templates
# using the familiar render_template() function. The templates receive the user and the token as arguments,
# so that a personalized email message can be generated.
def send_password_reset_email(user):
    # Get the token by utilizing the get_reset_password_token method from the user model
    token = user.get_reset_password_token()

    # Use the above function to compose and send an email using render template and users email address and token
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',    user=user, token=token),
               html_body=render_template('email/reset_password.html',   user=user, token=token))
