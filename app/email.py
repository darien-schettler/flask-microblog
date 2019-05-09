from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


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

    # The current_app._get_current_object() expression extracts the actual application instance from inside the proxy
    #  object, so that is what I passed to the thread as an argument.
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

# -------------------------------------------------------------------------------------------------------------------
