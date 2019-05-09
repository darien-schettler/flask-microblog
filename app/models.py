from datetime import datetime
from flask import current_app
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

# --Auxiliary Followers Table--
# Not declared in similar fashion to users and posts as followers is an auxiliary table and does not inherit base model
# Followers table is an example of a self-referential many-to-many relationship in which:
#   - A user (followed) may have many followers (follower)
#   - A user (follower) may follow many users (followed)
followers = db.Table('followers',
                     db.Column('follower_id',
                               db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id',
                               db.Integer,
                               db.ForeignKey('user.id')))


# ----- User Class -----
# Represents users on the blog
# Arguments are:
#   - UserMixin (Flask-Login provides a mixin class - includes generic implementations for most user model classes):
#       -->  is_authenticated : a property that is True if the user has valid credentials or False otherwise.
#       -->  is_active        : a property that is True if the user's account is active or False otherwise.
#       -->  is_anonymous     : a property that is False for regular users, and True for a special, anonymous user.
#       -->  get_id()         : a method that returns a unique identifier for the user as a string
#   - db.Model:
#       --> A base class for all models from Flask SQLAlchemy
class User(UserMixin, db.Model):
    # id is the PRIMARY KEY and is of d-type integer (will default to ascending digits auto-generated)
    id = db.Column(db.Integer, primary_key=True)

    # username is used to store the username is of d-type string with a max length of 64 chars (must be unique)
    username = db.Column(db.String(64), index=True, unique=True)

    # email is used to store user email-address and is of d-type string with a max length of 120 chars (must be unique)
    email = db.Column(db.String(120), index=True, unique=True)

    # password_hash is used to store the SH of the user's password it is of d-type string with a max length of 128 chars
    password_hash = db.Column(db.String(128))

    # posts is a high-level view of the relationship between the USERS & POSTS table. it is init with db.relationship()
    # For a one-to-many relationship, a db.relationship field is normally defined on the "one" side
    # A db.relationship is often used as a convenient way to get access to the "many" using this setup
    #   - The arg 'Post' is the model class that represents the "many" side of the relationship
    #   - The arg backref names a field added to the objects of the "many" class that points back at the "one" object
    #   - The arg lazy defines the db query for the relationship will be issued
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # ----------------------------- MANY-TO-MANY Relationship in the Users Table ------------------------------------
    #
    # The setup of the relationship is non-trivial. Like I did for the posts one-to-many relationship,
    # I'm using the db.relationship function to define the relationship in the model class.
    # This relationship links User instances to other User instances, so as a convention let's say that for a
    # pair of users linked by this relationship...
    #   --> THE LEFT SIDE USER IS FOLLOWING THE RIGHT SIDE USER
    # I'm defining the relationship as seen from the left side user with the name followed, because when I query this
    # relationship from the left side I will get the list of followed users (i.e those on the right side)
    #
    # ---------------- Let's Examine all the Arguments to the db.relationship() Call One-By-One ---------------------
    #
    #   'User'          -- The right side entity of the relationship (the left side entity is the parent class 'User')
    #                       - Since this is a self-referential relationship, I have to use the same class on both sides
    #
    #   secondary       -- Configures the association table that is used for this relationship
    #                       - This is defined right above this class (the auxiliary table defined at the top)
    #
    #   primaryjoin     -- Indicates the condition linking the left side entity (FOLLOWER) with the association table
    #                   -- The join condition for the left side of the relationship is the user ID matching the
    #                      follower_id field of the association table.
    #                       - The followers.c.follower_id references the follower_id column of the association table
    #
    #   secondaryjoin   -- Indicates the condition linking the right side entity (FOLLOWED) with the association table
    #                   -- This condition is similar to the one for primaryjoin
    #                       - The difference is now I'm using followed_id (other foreign key in the association table)
    #
    #   backref         -- Defines how this relationship will be accessed from the right side entity
    #                       - From the left side, the relationship is named followed
    #                       - For the right side I use the name followers to represent all the left side users
    #                          --> Left side users are linked to the target user on the right side
    #                   -- The additional lazy argument indicates the execution mode for this query.
    #                       - A mode of dynamic sets up the query to not run until specifically requested
    #                          --> This is also how I set up the posts one-to-many relationship
    #
    #   lazy            -- Similar to the parameter of the same name in the backref
    #                       - This parameter applies only to the left side query instead of the right side.
    #
    # ---------------------------------------------------------------------------------------------------------------

    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers',
                                                  lazy='dynamic'),
                               lazy='dynamic')

    # ---------------------------------------------------------------------------------------------------------------
    # Thanks to the SQLAlchemy ORM, a user following another user can be recorded in the database working with the
    # followed relationship as if it was a list. For example, if I had two users stored in user1 and user2 variables,
    #
    # I can make the first follow the second with this simple statement:
    #    >>> user1.followed.append(user2)
    #
    # To stop following the user, then I could do:
    #    >>> user1.followed.remove(user2)
    #
    # Even though adding and removing followers is fairly easy, I want to promote re-usability.
    # I'm going to implement the "follow" and "unfollow" functionality as methods
    # I'm doing this as it is best to keep application logic away from view functions
    #   --> keep logic within models or other auxiliary classes or modules
    #   --> This is because it makes unit testing easier
    # ---------------------------------------------------------------------------------------------------------------

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # ---------------------------------------------------------------------------------------------------------------
    # The follow() and unfollow() methods use the append() and remove() methods of the relationship object
    #
    # Before they touch the relationship they use the is_following() supporting method to make sure the requested
    # action makes sense.
    #
    #  For Example:  If I ask user1 to follow user2, but it turns out that this following relationship already exists
    #                in the database, I do not want to add a duplicate. The same logic can be applied to unfollowing.
    #
    # The is_following() method issues a query on the followed relationship to check if a link between two users
    # already exists. You have seen the filter_by() method of the SQLAlchemy query object before.
    #
    #  For Example:  To find a user given its username.
    #                The filter() method that I'm using here can include arbitrary filtering conditions unlike
    #                filter_by() which can only check for equality to a constant value.
    #
    # The condition that I'm using in is_following() looks for items in the association table that have
    # the left side foreign key set to the self user, and the right side set to the user argument.
    #
    # The query is terminated with a count() method, which returns the number of results.
    # The result of this query is going to be 0 or 1 (WE CAN USE =1 OR >0)
    #
    # NOTE: Other query terminators we have used are  all()  and  first()  .
    #
    # ---------------------------------------------------------------------------------------------------------------
    # ----------------------------------- Obtaining the Posts from Followed Users -----------------------------------
    #
    # This is by far the most complex query I have used on this application
    # I'm going to try to decipher this query one piece at a time.
    #
    # If you look at the structure of this query, you are going to notice that there are three main sections
    #
    #  1. join()   -->   method of the SQLAlchemy query object:
    #       - I'm invoking the join operation on the posts table. The first argument is the followers association table,
    #         and the second argument is the join condition. What I'm saying with this call is that I want the database
    #         to create a temporary table that combines data from posts and followers tables.
    #         The data is going to be merged according to the condition that I passed as argument.
    #       - The condition that I used says that the followed_id field of the followers table must be equal to
    #         the user_id of the posts table. To perform this merge, the database will take each record from the
    #         posts table (the left side of the join) and append any records from the
    #         followers table (the right side of the join) that match the condition.
    #         If multiple records in followers match the condition, then the post entry will be repeated for each.
    #         If for a given post there is no match in followers, then that post record is not part of the join.
    #
    #  2. filter()  -->  method of the SQLAlchemy query object:
    #       - I'm only interested in a subset of this list, the posts followed by a single user,
    #         so I need trim all the entries I don't need, which I can do with a filter() call.
    #       - Since this query is in a method of class User, the self.id expression refers to the user ID of the user
    #         I'm interested in. The filter() call selects the items in the joined table that have the follower_id
    #         column set to this user, which means that I'm keeping only the entries that have this user as a follower
    #       - Remember that the query was issued on the Post class, so even though I ended up with a temporary table
    #         that was created by the database as part of this query, the result will be the posts that are included
    #         in this temporary table, without the extra columns added by the join operation.
    #
    #  3. order_by() --> method of the SQLAlchemy query object:
    #       - The final step of the process is to sort the results
    #       - Here I'm saying that I want the results sorted by the timestamp field of the post in descending order.
    #         With this ordering, the first result will be the most recent blog post.
    #
    #  4. union()   -->  method of the SQLAlchemy query object:
    #       - Create a second query that returns the user's own posts
    #       - Use the "union" operator to combine the two queries into a single one
    #
    #       NOTE: union happens before sorting so posts aren't out of order
    #

    def followed_posts(self):
        followed = Post.query \
            .join(followers, (followers.c.followed_id == Post.user_id)) \
            .filter(followers.c.follower_id == self.id)

        own = Post.query.filter_by(user_id=self.id)

        return followed.union(own).order_by(Post.timestamp.desc())

    # ---------------------------------------------------------------------------------------------------------------

    # about_me is used to store additional user information and is of d-type string with a max length of 140 chars
    about_me = db.Column(db.String(140))

    # last_seen is used to store a timestamp (utc for now) that represents the last time the user accessed the site
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # .METHOD() to CREATE a hash for input password string received when a user is registering
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # .METHOD() to CHECK the hash for input password string against the stored password hash when user is logging-in
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # .METHOD() to CREATE/PASS an avatar from gravatar that is unique based upon the email of a given user (digest)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    # ---------------------------------- RESET PASSWORD TOKEN METHODS -----------------------------------------------
    #
    # Before I implement the send_password_reset_email() function, I need to have a way to generate a password
    # request link. This is going to be the link that is sent to the user via email. When the link is clicked,
    # a page where a new password can be set is presented to the user. The tricky part of this plan is to make sure
    # that only valid reset links can be used to reset an account's password.
    #
    # The links are going to be provisioned with a token, and this token will be validated before allowing the
    # password change, as proof that the user that requested the email has access to the email address on the
    # account. A very popular token standard for this type of process is the JSON Web Token, or JWT. The nice thing
    # about JWTs is that they are self contained. You can send a token to a user in an email, and when the user
    # clicks the link that feeds the token back into the application, it can be verified on its own
    #
    # ---------------------------------------------------------------
    #    Lets see an example as it would appear in a python shell:
    # ---------------------------------------------------------------
    #
    #   >>>   import jwt
    #
    #   >>>   token = jwt.encode({'a': 'b'}, 'my-secret', algorithm='HS256')
    #
    #   >>>   print(token)
    #         b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoiYiJ9.dvOo58OBDHiuSHD4uW88nfJikhYAXc_sfUHq1mDi4G0'
    #
    #   >>>   jwt.decode(token, 'my-secret', algorithms=['HS256'])
    #         {'a': 'b'}
    #
    # ---------------------------------------------------------------
    #
    # The {'a': 'b'} dictionary is an example payload that is going to be written into the token. To make the token
    # secure, a secret key needs to be provided to be used in creating a cryptographic signature. For this example I
    # have used the string 'my-secret', but with the application I'm going to use the SECRET_KEY from the
    # configuration. The algorithm argument specifies how the token is to be generated. The HS256 algorithm is the
    # most widely used.
    #
    # The resulting token is a long sequence of characters... BUT do not think that this is an encrypted token.
    # The contents of the token, including the payload, can be decoded easily by anyone using a JWT debugger.
    # What makes the token secure is that the payload is SIGNED. If somebody tried to forge/tamper with the payload
    # in a token, then the signature would be invalidated (and to generate a new signature the secret key is needed)
    # When a token is verified, the contents of the payload are decoded and returned back to the caller.
    # If the token's signature was validated, then the payload can be trusted as authentic.
    #
    # The payload that I'm going to use for the password reset tokens is going to have the format:
    #   --> {'reset_password': user_id, 'exp': token_expiration}
    #       - The exp field is standard for JWTs and if present it indicates an expiration time for the token
    #         If a token has a valid signature, but it is past its expiration timestamp, then it will also be
    #         considered invalid. For the password reset feature, I'm going to give these tokens 10 minutes of life.
    #
    # When the user clicks on the emailed link, the token is going to be sent back to the application as part of the
    # URL, and the first thing the view function that handles this URL will do is to verify it. If the signature is
    # valid, then the user can be identified by the ID stored in the payload. Once the user's identity is known,
    # the application can ask for a new password and set it on the user's account.
    #
    # Since these tokens belong to users, the token generation and verification functions are methods in the User model
    # ---------------------------------------------------------------------------------------------------------------

    # The get_reset_password_token() FN below generates a JWT token as a string.
    #   NOTE:  The decode('utf-8') is necessary because the jwt.encode() FN returns the token as a byte sequence, but
    #          in the application it is more convenient to have the token as a string.
    #
    #   NOTE:  The expiry is set to 600 which is 600 seconds or 10 minutes
    #
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # The @staticmethod decorator means that verify_reset_password_token is a STATIC METHOD
    # This means that it can be invoked directly from the class
    # A static method is similar to a class method, with the only difference that static methods do not receive
    # the class as a first argument.
    #
    # This method takes a token and attempts to decode it by invoking PyJWT's jwt.decode() function.
    # If the token cannot be validated or is expired, an exception will be raised, and in that case I catch it
    # to prevent the error, and then return None to the caller. If the token is valid, then the value of the
    # reset_password key from the token's payload is the ID of the user, so I can load the user and return it.
    #
    #   NOTE:  try/except sequence is used to 'catch' the token only if it cannot be validated (prevents error screen)
    #          It should be specific to the encountered error to prevent generalization
    @staticmethod
    def verify_reset_password_token(token):

        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return

        return User.query.get(id)

    # ---------------------------------------------------------------------------------------------------------------

    # .METHOD() to TELL Python how to print objects of this class, which is going to be useful for debugging
    def __repr__(self):
        return '<User {}>'.format(self.username)


# ------------------------------------- RELATIONSHIP BETWEEN USERS & POSTS ---------------------------------------
#   The way to link a blog post to the user that authored it is to add a reference to the user's id, and that is
# exactly what the user_id field is. This user_id field is called a foreign key. The database diagram above shows
# foreign keys as a link between the field and the id field of the table it refers to. This kind of relationship is
# called a one-to-many, because "one" user writes "many" posts.
# ----------------------------------------------------------------------------------------------------------------


# ----- POSTS CLASS -----
# Represents blog posts written by users
# Arguments are:
#   - db.Model:
#       --> A base class for all models from Flask SQLAlchemy
class Post(db.Model):
    # id is the PRIMARY KEY and is of d-type integer (will default to ascending digits auto-generated)
    id = db.Column(db.Integer, primary_key=True)

    # body is used to store the post body-text and is of d-type string with a max length of 140 chars
    body = db.Column(db.String(140))

    # timestamp is used to store the time a post was created/edited (default is manually set to utc-now fn)(index-able)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # user_id initialized as a FOREIGN KEY to user.id (references id value from USERS table)(requires db.relationship())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# -----FLASK-LOGIN EXTENSION-----
# Works with the application's user model and expects certain properties and methods to be implemented (UserMixin)
#
# Flask-Login keeps track of the logged in user by storing its unique identifier in Flask's user session,
# A user session is a  storage space assigned to each user who connects to the application
#
# Each time the logged-in user navigates to a new page, Flask-Login retrieves the ID of the user from the session,
# and then loads that user into memory.
#
# ----- USER LOADER FN -----
#
# Because Flask-Login knows nothing about databases, it needs the application's help in loading a user.
# For that reason, the extension expects that the application will configure a user loader function, that can be called
# to load a user given the ID.


# The user loader is registered with Flask-Login with the @login.user_loader decorator
@login.user_loader
def load_user(id):
    return User.query.get(int(id))  # DB may use numeric ID hence the int conversion
