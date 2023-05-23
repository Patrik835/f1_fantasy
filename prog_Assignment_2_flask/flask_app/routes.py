from flask import render_template, flash, redirect, url_for, session
from flask_app.models import Users, QuizAnswers
from flask_app.forms import LoginForm, RegisterForm, QuizForm
from flask_app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


#flask login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    #validate form
    if form.validate_on_submit():           
        user = Users.query.filter_by(username=form.username.data, email=form.email.data, password = form.password.data).first()  # check if user exists
        if user is None:                                                                          # if not, create new user
            #hash the password
            hash_pw = generate_password_hash(form.password.data, 'SHA256')
            user = Users(username = form.username.data, email = form.email.data, password_hash = hash_pw)  # create new user
            db.session.add(user)                # add new user to database
            db.session.commit()                 # commit changes to database
            flash("You have successfully registered")
            return redirect(url_for('dashboard'))
        else:
            flash("Username or email already exists")
    return render_template("register.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    #validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()  # check if user exists
        if user and check_password_hash(user.password_hash, form.password.data):   #check if password is correct
            login_user(user)                  # log in the user
            flash("You have successfully logged in")
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
                session['logged_in'] = False
                flash(f"Password or username is incorrect - Try again")
    return render_template("login.html", form = form)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    flash("You have successfully logged out")
    return redirect(url_for('login'))

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    user_to_delete_2 = QuizAnswers.query.get_or_404(id)
    username = None
    form = LoginForm()
    try:
        db.session.delete(user_to_delete)
        db.session.delete(user_to_delete_2)
        db.session.commit()
        flash("User successfully deleted")
        our_users = Users.query.order_by(Users.date_created)
        return render_template("admin.html",form=form, username = username, our_users = our_users)
    except:
        flash("There was a problem deleting that user")
        return render_template("admin.html",form=form, username = username)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/quiz_form", methods=["GET", "POST"])
@login_required
def quiz_form():
    form = QuizForm()
    user_quiz = QuizAnswers.query.get(current_user.id)
    if not user_quiz:
        user_quiz = QuizAnswers(user_id=current_user.id)  # Create a new QuizAnswers object
    if form.validate_on_submit():
        user_quiz.q1 = form.q1.data
        user_quiz.q2 = form.q2.data
        user_quiz.q3 = form.q3.data
        user_quiz.q4 = form.q4.data
        user_quiz.q5 = form.q5.data
        user_quiz.q6 = form.q6.data
        user_quiz.q7 = form.q7.data
        user_quiz.q8 = form.q8.data
        user_quiz.q9 = form.q9.data
        user_quiz.q10 = form.q10.data
        user_quiz.q11 = form.q11.data
        db.session.add(user_quiz)
        db.session.commit()
        flash("You have successfully completed the quiz")
        return redirect(url_for('dashboard'))
    return render_template("quiz_form.html", form = form)

@app.route("/user_standings")
def user_standings():
    our_users = Users.query.order_by(Users.date_created)
    return render_template("tables.html",our_users = our_users)

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id ==1:
        our_users = Users.query.order_by(Users.date_created)
        return render_template("admin.html",our_users = our_users)
    else:
        flash("You do not have access to this page, must be admin")
        return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")