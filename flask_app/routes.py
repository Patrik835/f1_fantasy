from flask import render_template, flash, redirect, url_for, session
from flask_app.models import Users, QuizAnswers
from flask_app.forms import LoginForm, RegisterForm, QuizForm
from flask_app.scraper import answers_list, get_number_of_the_race
from flask_app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta

#flask login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

#index page
@app.route("/")
def index():
    #getting needed values from the function
    next_race, race_nr, race_d = get_number_of_the_race()
    deadline_date = race_d - timedelta(days=1)
    #rendering the page with values
    return render_template("index.html", next_race = next_race, race_nr = race_nr, race_d = race_d, deadline_date = deadline_date)
#register page
@app.route("/register", methods=["GET", "POST"])
def register():
    #get the form
    form = RegisterForm()
    #validate form
    if form.validate_on_submit():
        #get users from db table to check if user exists
        user = Users.query.filter_by(username=form.username.data, email=form.email.data, password = form.password.data).first()  
        #if does not exist, create new user
        if user is None:
            #hash the password
            hash_pw = generate_password_hash(form.password.data, 'SHA256')
            # create new user
            user = Users(username = form.username.data, email = form.email.data, password_hash = hash_pw)
            db.session.add(user)             # add new user to database
            db.session.commit()              # commit changes to database
            flash("You have successfully registered")
            return redirect(url_for('dashboard'))
        else:
            flash("Username or email already exists")
    return render_template("register.html", form = form)
#log in page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    #validate form
    if form.validate_on_submit():
        # check if user exists
        user = Users.query.filter_by(username=form.username.data).first()
        #check if password is correct
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)                  # log in the user
            flash("You have successfully logged in")
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        #if pasword or username is incorrect
        else:
                session['logged_in'] = False
                flash(f"Password or username is incorrect - Try again")
    return render_template("login.html", form = form)
#log out page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    flash("You have successfully logged out")
    return redirect(url_for('login'))

@app.route("/delete_all_inputs", methods=["GET", "POST"])
@login_required
def delete_all_inputs():
    id = current_user.id
    if id == 1: 
        try:
            db.session.query(QuizAnswers).delete()
            db.session.commit()
            flash("All inputs deleted successfully")
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f"error{e}")
            return redirect(url_for('admin'))
    else:
        flash("You do not have access to this page, must be admin")
        return redirect(url_for('dashboard'))
    
@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    id = current_user.id
    if id == 1: 
        user_to_delete = Users.query.get_or_404(id)
        try:
            user_to_delete_2 = QuizAnswers.query.get_or_404(id)
        except:
            user_to_delete_2 = None
        username = None
        form = LoginForm()
        try:
            db.session.delete(user_to_delete)
            if user_to_delete_2 != None:
                db.session.delete(user_to_delete_2)
            db.session.commit()
            flash("User successfully deleted")
            our_users = Users.query.order_by(Users.date_created)
            return render_template("admin.html",form=form, username = username, our_users = our_users)
        except:
            flash("There was a problem deleting that user")
            return render_template("admin.html",form=form, username = username)
    else:
        flash("You do not have access to this page, must be admin")
        return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    current_answers = QuizAnswers.query.get(current_user.id)
    return render_template("dashboard.html" , current_answers = current_answers)

@app.route("/quiz_form", methods=["GET", "POST"])
@login_required
def quiz_form():
    next_race, race_nr, race_d = get_number_of_the_race()
    today = datetime.now().date()
    if  today == race_d:
        flash("Deadline for quiz has passed, try again next week!")
        return redirect(url_for('index'))
    else:
        form = QuizForm()
        user_quiz = QuizAnswers.query.get(current_user.id)
        if user_quiz:
            form.q1.default = user_quiz.q1
            form.q2.default = user_quiz.q2
            form.q3.default = user_quiz.q3
            form.q4.default = user_quiz.q4
            form.q5.default = user_quiz.q5
            form.q6.default = user_quiz.q6
            form.q7.default = user_quiz.q7
            form.q8.default = user_quiz.q8
            form.q9.default = user_quiz.q9
            form.q10.default = user_quiz.q10
            form.q11.default = user_quiz.q11
            form.q12.default = user_quiz.q12
            form.process()
        else:
            pass
        if not user_quiz:
            user_quiz = QuizAnswers(user_id=current_user.id)  # Create a new QuizAnswers object
        if form.validate_on_submit():
            form = QuizForm()
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
            user_quiz.q12 = form.q12.data
            db.session.add(user_quiz)
            db.session.commit()
            flash("You have successfully completed the quiz")
            return redirect(url_for('dashboard'))
        return render_template("quiz_form.html", form = form, next_race = next_race, race_nr=race_nr)

@app.route("/user_standings")
@login_required
def user_standings():
    our_users = Users.query.order_by(Users.points.desc())
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
    
@app.route("/evaluation")
@login_required
def evaluation():
    id = current_user.id
    if id == 1:       
        evaluated_answers = answers_list()  
        answers = QuizAnswers.query.all()
        for answer in answers:
            points = 0
            if answer.q1 == evaluated_answers[0]:
                points += 2
            elif answer.q1 != evaluated_answers[0]:
                points -= 1
            if answer.q2 == evaluated_answers[1]:
                points += 2
            elif answer.q2 != evaluated_answers[1]:
                points -= 1
            if answer.q3 == evaluated_answers[2]:
                points += 2
            elif answer.q3 != evaluated_answers[2]:
                points -= 1
            if answer.q4 == evaluated_answers[3]:
                points += 2
            elif answer.q4 != evaluated_answers[3]:
                points -= 1
            if answer.q5 in evaluated_answers[4]:
                points += 2
            elif len(evaluated_answers[5]) == 0 and answer.q5 == 'nobody':
                points += 2
            elif answer.q5 not in evaluated_answers[4]:
                points -= 1
            if answer.q6 == evaluated_answers[5]:
                points += 2
            elif answer.q6 != evaluated_answers[5]:
                points -= 1
            if answer.q7 == evaluated_answers[6]:
                points += 2
            elif answer.q7 == 'unanswered':
                points += 0
            else:
                points -= 1
            if answer.q8 == evaluated_answers[7]:
                points += 2
            elif answer.q8 == 'unanswered':
                points += 0
            else:
                points -= 1
            if answer.q9 == evaluated_answers[8]:
                points += 2
            elif answer.q9 == 'unanswered':
                points += 0
            else:
                points -= 1
            if answer.q10 == evaluated_answers[9]:
                points += 2
            if answer.q11 == evaluated_answers[10]:
                points += 2
            if answer.q12 == evaluated_answers[11]:
                points += 2
            if points < 0:
                points == 0
            id = answer.user_id
            user = Users.query.get_or_404(id)
            user.points += points
            db.session.commit()
        return render_template("admin.html")
    else:
        flash("You do not have access to this page, must be admin")
        return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")