import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


# This class is used to control the SQLAlchemy integration to one or more Flask applications. Depending on how you
# initialize the object it is usable right away or will attach as needed to a Flask application.
#
# The usage mode which is utilized involves binding the instance to a very specific Flask application:
db = SQLAlchemy()

# Sentry extension
sentry_sdk.init(
    dsn="https://b4fd20a1b0d34a6abefbda5c324aaefc@sentry.io/1456192",
    integrations=[FlaskIntegration()])

# Flask-Migrate is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic. The
# database operations are made available through the Flask command-line interface or through the Flask-Script
# extension. This is utilizing the Flask-Script exposing the database migrations.
migrate = Migrate()

# The most important part of an application that uses Flask-Login is the LoginManager class. The login manager
# contains the code that lets your application and Flask-Login work together, such as how to load a user from an ID,
# where to send users when they need to log in, and the like.
# By default, when a user attempts to access a login_required view without being logged in, Flask-Login will flash a
# message and redirect them to the log in view. (If the login view is not set, it will abort with a 401 error.)
login = LoginManager()


# The name of the log-in view is set below using the pre .html part of the name from the templates/auth folder
login.login_view = 'auth.login'

login.login_message = "Please Log-In To Access This Page"

# Flask-Mail is an extension to provide a simple interface to set up SMTP with your Flask app to send messages from
# your views, and scripts. A web based application is often required to have a feature of sending mail to the
# users/clients. The Flask-Mail extension makes it very easy to set up a simple interface with any email server.
mail = Mail()


# Flask-Moment is an extension for formatting of dates and times in Flask templates using moment.js
# Since this extension is dependant upon moment.js it must ALWAYS be imported
moment = Moment()


# Flask-Bootstrap packages Bootstrap into an extension that mostly consists of a blueprint named ‘bootstrap’.
# It can also create links to serve Bootstrap from a CDN
# This extension is for styling and responsive web design
bootstrap = Bootstrap()


# Flask-Babel is an extension to Flask that adds i18n and l10n support to any Flask application with the help of
# babel, pytz and speaklater. It has builtin support for date formatting with timezone support as well as a very
# simple and friendly interface to gettext translations.
babel = Babel()


def create_app(config_class=Config):
    # An "application" will exist in a package
    # In Python, a sub-directory that includes a __init__.py file is considered a package, and can be imported
    # When importing a package, the __init__.py executes & defines what symbols the package exposes to the world

    # One aspect that may seem confusing at first is that there are two entities named app.
    # The app PACKAGE is defined by the app dir and the __init__.py script (referenced in the app import statement)
    # The app VARIABLE is defined as an instance of class Flask in the __init__.py script, (it is a part of the package)

    # Create the application object as an instance of class Flask imported from the flask package
    app = Flask(__name__)

    # Applications need some kind of configuration. There are different settings you might want to change depending on
    # the application environment like toggling the debug mode, setting the secret key, and other such
    # environment-specific things.
    #
    # The way Flask is designed usually requires the configuration to be available when the application starts up. You
    # can hardcode the configuration in the code, which for many small applications is not actually that bad,
    # but there are better ways.
    #
    # Independent of how you load your config, there is a config object available which holds the loaded configuration
    # values: The config attribute of the Flask object. This is the place where Flask itself puts certain configuration
    # values and also where extensions can put their configuration values. But this is also where you can have your own
    # configuration. This is how we load values into the app's configuration.
    #
    # Configuration becomes more useful if you can store it in a separate file, ideally located outside the actual
    # application package. This makes packaging and distributing your application possible via various package handling
    # tools (Deploying with Setuptools) and finally modifying the configuration file afterwards.
    app.config.from_object(config_class)

    # You have seen that most Flask extensions are initialized by creating an instance of the extension and passing
    # the application as an argument. When the application does not exist as a global variable, there is an
    # alternative mode in which extensions are initialized in two phases. The extension instance is first created in
    # the global scope as before, but no arguments are passed to it. This creates an instance of the extension that
    # is not attached to the application. At the time the application instance is created in the factory function,
    # the init_app() method must be invoked on the extension instances to bind it to the now known application.
    #
    # Other tasks performed during initialization remain the same, but are moved to the factory function instead of
    # being in the global scope. This includes the registration of blueprints and logging configuration. Note that I
    # have added a not app.testing clause to the conditional that decides if email and file logging should be enabled
    #  or not, so that all this logging is skipped during unit tests. The app.testing flag is going to be True when
    # running unit tests, due to the TESTING variable being set to True in the configuration.
    #
    # ----------------------------------------------------------------------------------------------------------------
    #
    # So who calls the application factory function? The obvious place to use this function is the top-level
    # microblog.py script, which is the only module in which the application now exists in the global scope. The
    # other place is in tests.py, and I will discuss unit testing in more detail in the next section.
    #
    # As I mentioned above, most references to app went away with the introduction of blueprints, but there were some
    # still in the code that I had to address. For example, the app/models.py, app/translate.py,
    # & app/main/routes.py modules all had references to current_app.config. Fortunately, the Flask developers tried to
    # make it easy for view functions to access the application instance without having to import it like I have been
    # doing until now. The current_app variable that Flask provides is a special "context" variable that Flask
    # initializes with the application before it dispatches a request. You have already seen another context variable
    # before, the g variable in which I'm storing the current locale. These two, along with Flask-Login's
    # current_user and a few others you haven't seen yet, are somewhat "magical" variables, in that they work like
    # global variables, but are only accessible during the handling of a request, and only in the thread that is
    # handling it.

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # To register a blueprint, the register_blueprint() method of the Flask application instance is used. When a
    # blueprint is registered, any view functions, templates, static files, error handlers, etc. are connected to the
    # application. Import of the blueprint goes right above the app.register_blueprint() to avoid circular dependencies.
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # The register_blueprint() call in this case has an extra argument, url_prefix. This is entirely optional,
    # Flask gives you the option to attach a blueprint under a URL prefix, so any routes defined in the blueprint get
    # this prefix in their URLs. In many cases this is useful as a sort of "namespacing" that keeps all the routes in
    # the blueprint separated from other routes in the application or other blueprints. For authentication, I thought it
    # was nice to have all the routes starting with /auth, so I added the prefix. So now the login URL is going to be
    # http://localhost:5000/auth/login. Because I'm using url_for() to generate the URLs, all URLs will automatically
    # incorporate the prefix.
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # The third blueprint contains the core application logic. Refactoring this blueprint requires the same process that
    # I used with the previous two blueprints. I gave this blueprint the name main, so all url_for() calls that
    # referenced view functions had to get a main. prefix. Given that this is the core functionality of the application,
    # I decided to leave the templates in the same locations. This is not a problem because I have moved the templates
    # from the other two blueprints into sub-directories
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # I'm only going to enable the email logger when the application is running without debug mode, indicated by
    # app.debug being True, and also when the email server exists in the configuration.
    #
    # Setting up the email logger is somewhat tedious due to having to handle optional security options that are present
    # in many email servers. But in essence, the code below creates a SMTPHandler instance, sets its level so that it
    # only reports errors and not warnings, informational or debugging messages, and finally attaches it to the
    # app.logger object from Flask.
    if not app.debug and not app.testing:
        # EXPLAIN FURTHER
        if app.config['MAIL_SERVER']:

            auth = None

            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None

            if app.config['MAIL_USE_TLS']:
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)

            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Receiving errors via email is nice, but sometimes this isn't enough. There are some failure conditions
        # that do not end in a Python exception and are not a major problem, but they may still be interesting enough to
        # save for debugging purposes. For this reason, I'm also going to maintain a log file for the application.
        #
        # To enable a file based log another handler, this time of type RotatingFileHandler, needs to be attached to the
        # application logger, in a similar way to the email handler.
        #
        # Write the log file with name microblog.log in a logs directory, which I create if it doesn't already exist.
        #
        # The RotatingFileHandler class is nice because it rotates the logs, ensuring that the log files do not grow too
        # large when the application runs for a long time. In this case I'm limiting the size of the log file to 10KB,
        # and I'm keeping the last ten log files as backup.
        #
        # The logging.Formatter class provides custom formatting for the log messages. Since these messages are going to
        # a file, I want them to have as much information as possible.I'm using a format that includes the timestamp,
        # the logging level, the message and the source file and line number from where the log entry originated.
        #
        # To make the logging more useful, I'm also lowering the logging level to the INFO category, both in the
        # application logger and the file logger handler. In case you are not familiar with the logging categories,
        # they are DEBUG, INFO, WARNING, ERROR and CRITICAL in increasing order of severity.
        #
        # As a use of the log file, the server writes a line to the logs each time it starts. When this
        # application runs on a production server, these log entries will tell you when the server was restarted.
        if not os.path.exists('logs'):

            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                                    '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Acorn's Microblog startup")

    return app

# -------------------------------------------------------------------------------------------------------------------

# The Babel instance provides a localeselector decorator. The decorated function is invoked for each request to
# select a language translation to use for that request:
#
# NOTE ON BABEL: I skipped full babel integration ... can be added later (XIII)
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

# Here I'm using an attribute of Flask's request object called accept_languages. This object provides a high-level
# interface to work with the Accept-Language header that clients send with a request. This header specifies the
# client language and locale preferences as a weighted list. The contents of this header can be configured in the
# browser's preferences page, with the default being usually imported from the language settings in the computer's
# operating system. Most people don't even know such a setting exists, but this is useful as users can provide a list
#  of preferred languages, each with a weight.
# -------------------------------------------------------------------------------------------------------------------


# The bottom import is a workaround to circular imports, a common problem with Flask applications.
# You are going to see that the routes module needs to import the app variable defined in this script
# Therefore, putting one of the reciprocal imports at the bottom will avoid the error
#   - As the error would have resulted from the mutual references between these two files
from app import models
