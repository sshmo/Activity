from flask import Blueprint, redirect, render_template, session, request, Flask, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from .models import User
from . import db

from .apology import apology

auth = Blueprint('auth', __name__)
activities = []


@auth.route('/login', methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("username")
        # Ensure username was submitted
        if not name:
            flash('Must provide username.')
            return redirect(url_for('auth.login'))

        password = request.form.get("password")
        # Ensure password was submitted
        if not password:
            flash('Must provide password.')
            return redirect(url_for('auth.login'))

        # Query database for username
        user = User.query.filter_by(user_name=name).first()

        # check if user actually exists
        # take the user supplied password, hash it, and compare it to the hashed password in database
        if not user or not check_password_hash(user.user_hash, password):
            flash('Please check your login details and try again.')
            # if user doesn't exist or password is wrong, reload the page
            return redirect(url_for('auth.login'))

        # if the above check passes, then we know the user has the right credentials
        # Trigger db update for automatic lastlogin update
        if user.log_update == True:
            user.log_update = False
        else:
            user.log_update = True
        db.session.commit()

        login_user(user)

        flash("You are now logged in!")
        return redirect('/profile')

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template('login.html')


@auth.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget user
    logout_user()

    # Redirect user to login form
    flash("logged out!")
    return redirect('/login')


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("username")

        # Ensure username was submitted
        if not name:
            flash('Must provide username.')
            return redirect(url_for('auth.register'))

        # Query database for username
        user = User.query.filter_by(user_name=name).first()

        # Ensure username does not exists
        if user:
            flash('Username not available.')
            return redirect(url_for('auth.register'))

        password = request.form.get("password")

        # Ensure password was submitted
        if not password:
            flash('Must provide password')
            return redirect(url_for('auth.register'))

        conf = request.form.get("confirmation")

        # Ensure password was submitted again
        if not conf:
            flash("Must provide Password (again)")
            return redirect(url_for('auth.register'))

        # Ensure password and confirmation passord match
        if not (password == conf):
            flash("Passwords don't match!")
            return redirect(url_for('auth.register'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(user_name=name, user_hash=generate_password_hash(
            password, method='sha256'))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash("You are now registered!")
        return redirect('/login')

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template('register.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    auth.errorhandler(code)(errorhandler)
