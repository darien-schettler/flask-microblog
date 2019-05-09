from flask import render_template
from app import db
from app.errors import bp

# Flask provides a mechanism for an application to install its own error pages, so that your users don't have to see
# the plain and boring default ones. As an example, let's define custom error pages for the HTTP errors 404 and 500,
# the two most common ones. Defining pages for other errors works in the same way.
#
# To declare a custom error handler, the @errorhandler decorator is used.
#
# The error functions work very similarly to view functions. For these two errors, I'm returning the contents of
# their respective templates. Note that both functions return a second value after the template, which is the error
# code number. For all the view functions that I created so far, I did not need to add a second return value because
# the default of 200 (the status code for a successful response) is what I wanted. In this case these are error
# pages, so I want the status code of the response to reflect that.


# Error function for 404 error
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


# Error function for 500 error
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
