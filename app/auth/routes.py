from flask import render_template, flash, redirect, url_for, request
from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


# @ symbol indicates what is known as a decorator (i.e. @app.route, or @login_required):
#   - A decorator modifies the FN that follows it
#   - A common pattern with decorators is to use them to register FNs as callbacks for certain events.

# The methods argument included in this decorator app.route indicates that...
#   - this view function accepts GET and POST requests, overriding the default, which is to accept only GET requests.
#       - GET request  --> Return information to the client (the web browser in this case)
#       - POST request --> Typically used when the browser submits form data to the server
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Checks to make sure the current_user is logged-in... if so than they shouldn't be here and redirect home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Above in the imports the LoginForm() class was imported from forms.py and we are instantiating an object (form)
    form = LoginForm()

    # The form.validate_on_submit() method does all the form processing work. When the browser sends the GET request
    # to receive the web page with the form, this method is going to return False, so in that case the function skips
    # the if statement and goes directly to render the template in the last line of the function.
    #
    # When the browser sends the POST request as a result of the user pressing the submit button,
    # form.validate_on_submit() is going to gather all the data, run all the validators attached to fields,
    # and if everything is all right it will return True, indicating that the data is valid and can be processed by
    # the application. But if at least one field fails validation, then the function will return False, and that will
    # cause the form to be rendered back to the user, like in the GET request case. This is also where we render error
    # messages when validation fails.
    #
    # When form.validate_on_submit() returns True, the login view function calls two new functions, imported from
    # Flask. The flash() function is a useful way to show a message to the user. A lot of applications use this
    # technique to let the user know if some action has been successful or not.
    if form.validate_on_submit():
        # Return the matching user object resulting from a db query using the form username data
        user = User.query.filter_by(username=form.username.data).first()

        # If the function returns FALSE when checking the user entered password (or nothing is entered) flash is used
        # to display an error message to the user and to redirect/refresh the login page
        #
        # When the Flask Class's redirect FN is called, it returns a response object and redirects the user to another
        # target location with specified status code.
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        # This FN comes from Flask-Login & will register the user as logged in
        # This means that any future pages the user navigates to will have the current_user variable set to that user
        login_user(user, remember=form.remember_me.data)

        # If there is a next_page stored than the user will be redirected there... if not then to the index page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    # In this case we return the html template for the login screen along with the appropriate title and form data
    return render_template('auth/login.html', title='Sign In', form=form)


# This is the FN for logging out that is associated with the /logout address request
# The logout_user() FN is from Flask-Login and will remove authentication and redirect to the home page
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# This is the FN for registering that is associated with the /register address request
# FN accepts both GET & POST requests
# noinspection PyArgumentList
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Check that user isn't logged in... if they are than get them off of this page (they shouldn't be here obv.)
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Above in the imports the RegistrationForm() class was imported and we are instantiating an object (form)
    form = RegistrationForm()

    # Validate the form submission as explained above
    if form.validate_on_submit():
        # Instantiate a user object from the User class with the username/email given from the form data
        user = User(username=form.username.data, email=form.email.data)

        # Update the password field of the user object using the password given from the form data
        user.set_password(form.password.data)

        # Add and commit the changes to the database
        db.session.add(user)
        db.session.commit()

        # Show the user a message letting them know that the operation was performed successfully
        flash('Congratulations, you are now a registered user!')

        # Redirect the user to the login screen so that they can use their newly created credentials to log in
        return redirect(url_for('auth.login'))

    # Return the html for the register page is validation fails with the appropriate title and form
    return render_template('auth/register.html', title='Register', form=form)


# This is the FN for sending a request to reset a users password (as such no login is required)
# It is associated with the /reset_password_request path
# This function accepts both HTTP GET & POST requests
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # Check to make sure that the user isn't logged in and has stumbled to this page... if so redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Import the appropriate form object that was defined in forms.py (ResetPasswordRequestForm())
    form = ResetPasswordRequestForm()

    # Check for validation on submit and if successful (if email entered exists) than send password reset email
    # Additionally we will display a success message and redirec the user to the login page & display errors (inherent)
    # If they fail validation than simply reload the current page
    if form.validate_on_submit():
        # set the user variable to be the first returned match for the passed user argument
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            send_password_reset_email(user)

        # You may notice that the flashed message below is displayed even if the email provided by the user is unknown.
        # This is so that clients cannot use this form to figure out if a given user is a member or not.
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


# This is the FN called when a user clicks the password reset link from within their email
# This FN is associated with the /reset_password/<token> path (uses the token included in the sent email)
# As this function is being launched from an external site no authorization is required (not logged in)
# This function accepts both HTTP GET & POST requests
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check to make sure that the user isn't logged in and has stumbled to this page... if so redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # determine who the user is by invoking the token verification method in the User class. This method returns the
    # user if the token is valid, or None if not. If the token is invalid I redirect to the home page.
    user = User.verify_reset_password_token(token)

    # If the token above is invalid than redirect the user to the homepage
    if not user:
        return redirect(url_for('main.index'))

    # If the token checked above is valid, present the user with a second form, in which the new password is requested
    # Import the appropriate form object that was defined in forms.py (ResetPasswordForm())
    form = ResetPasswordForm()

    # This form is processed in a way similar to previous forms, and as a result of a valid form submission,
    # I invoke the set_password() method of User to change the password, and then redirect to the login page,
    # where the user can now login. I also display a success message to communicate with the user a successful change
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))

    # If form fails to validate than refresh the page
    return render_template('auth/reset_password.html', form=form)
