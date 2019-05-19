from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fitness.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    #if request.form.get("submit"):


    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return redirect("/login")
            flash("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            flash("must provide username")

        rows = db.execute("SELECT * FROM users WHERE email = :email", email = request.form.get("email"))
        if len(rows) > 1:
            flash("Sorry that email is already in use")

        elif not request.form.get("password"):
            flash("must provide password")

        elif not request.form.get("confirmation"):
            flash("please confirm pasword")

        elif not request.form.get("email"):
            flash("please enter a vaild email")

        elif request.form.get("confirmation") != request.form.get("password"):
            flash("passwords must match")

        else:
            hash = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)", username = request.form.get("username"), email = request.form.get("email"), password = hash)
            flash("YOU HAVE REGISTERED")
            return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/about")
@login_required
def about():

    return render_template("about_us.html")

@app.route("/#")
@login_required
#send email with password to user who gives email or username
def forgot():

    return render_template("forgot.html")