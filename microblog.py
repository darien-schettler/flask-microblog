from app import create_app, db
from app.models import User, Post

# FN called create_app() that constructs a Flask application instance, and eliminate the global variable
app = create_app()


# Python script at the top-level that defines the Flask application instance
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
