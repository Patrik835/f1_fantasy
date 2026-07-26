from flask import render_template, flash, redirect, url_for, request
from flask_app.models import User, Role, Race, Prediction
from flask_app.forms import LoginForm, RegisterForm, PredictionForm, AdminUserForm
from flask_app.api_service import JolpiErgastAPI
from flask_app import app, db
from flask_app.time_utils import parse_api_datetime, prediction_deadline, to_utc_aware, to_utc_naive, utc_now
from flask_login import login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_rank():
    ranked_users = User.query.order_by(User.points.desc(), User.username.asc()).all()
    for index, user in enumerate(ranked_users, start=1):
        if user.id == current_user.id:
            return index
    return None


def get_race_status(race):
    if race.is_completed:
        return "Completed"
    if to_utc_aware(race.race_date) < utc_now():
        return "Finished"
    return "Upcoming"


def build_admin_form():
    form = AdminUserForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
    return form


def driver_number(result):
    driver = result.get('Driver') or {}
    return driver.get('permanentNumber') or driver.get('driverId')


def constructor_id(result):
    constructor = result.get('Constructor') or {}
    return constructor.get('constructorId')


def numeric_points(result):
    try:
        return float(result.get('points', 0) or 0)
    except (TypeError, ValueError):
        return 0


def did_not_finish(result):
    status = (result.get('status') or '').strip().lower()
    position_text = result.get('positionText')
    return status not in {'finished', '+1 lap', '+2 laps'} and position_text == 'R'


def build_actual_results(race_results):
    results = (race_results or {}).get('Results') or []
    classified_results = [result for result in results if driver_number(result)]
    if len(classified_results) < 3:
        return None

    team_points = {}
    for result in classified_results:
        team = constructor_id(result)
        if team:
            team_points[team] = team_points.get(team, 0) + numeric_points(result)

    fastest_lap = next(
        (
            driver_number(result)
            for result in classified_results
            if (result.get('FastestLap') or {}).get('rank') == '1'
        ),
        None,
    )
    dnf = next((driver_number(result) for result in classified_results if did_not_finish(result)), None)

    return {
        'p1': driver_number(classified_results[0]),
        'p2': driver_number(classified_results[1]),
        'p3': driver_number(classified_results[2]),
        'last_place': driver_number(classified_results[-1]),
        'dnf': dnf,
        'fastest_lap': fastest_lap,
        'team_podium': constructor_id(classified_results[0]),
        'team_most_points': max(team_points, key=team_points.get) if team_points else None,
        'safety_car': 'no',
        'red_flag': 'no',
        'wet_race': 'no',
    }


def score_prediction(prediction, actual_results):
    points = 0
    scoring_rules = {
        'p1': 3,
        'p2': 3,
        'p3': 3,
        'last_place': 2,
        'dnf': 2,
        'fastest_lap': 2,
        'team_podium': 2,
        'team_most_points': 2,
        'safety_car': 1,
        'red_flag': 1,
        'wet_race': 1,
    }
    for field, field_points in scoring_rules.items():
        actual_value = actual_results.get(field)
        if actual_value is not None and getattr(prediction, field) == actual_value:
            points += field_points
    return points

@app.route("/")
def index():
    next_race = JolpiErgastAPI.get_next_race()
    if next_race:
        race_date = parse_api_datetime(next_race.get('date_start'))
        if not race_date:
            return render_template("index.html", next_race=None)
        deadline_date = prediction_deadline(race_date)
        current_date = utc_now()
        time_until_race = race_date - current_date
        
        # Calculate days, hours, and minutes
        days = time_until_race.days
        hours = time_until_race.seconds // 3600
        minutes = (time_until_race.seconds % 3600) // 60
        
        countdown = f"{days} days, {hours} hours, and {minutes} minutes"
        
        return render_template("index.html", 
                             next_race=next_race['meeting_name'],
                             race_date=race_date,
                             deadline_date=deadline_date,
                             countdown=countdown)
    return render_template("index.html", next_race=None)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Get the default user role
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                user_role = Role(name='user')
                db.session.add(user_role)
                db.session.commit()

            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=user_role
            )
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    next_race = JolpiErgastAPI.get_next_race()
    if next_race:
        race_date = parse_api_datetime(next_race.get('date_start'))
        if not race_date:
            return render_template("dashboard.html", next_race=None, current_user_rank=get_current_user_rank())
        deadline_date = prediction_deadline(race_date)
        
        # Get user's prediction for next race if exists
        race = Race.query.filter_by(meeting_key=next_race['meeting_key']).first()
        if not race:
            race = Race(
                meeting_key=next_race['meeting_key'],
                race_name=next_race['meeting_name'],
                race_date=to_utc_naive(race_date)
            )
            db.session.add(race)
            db.session.commit()
        
        prediction = Prediction.query.filter_by(
            user_id=current_user.id,
            race_id=race.id
        ).first()
        
        return render_template("dashboard.html",
                             next_race=race,
                             deadline_date=deadline_date,
                             prediction=prediction,
                             current_user_rank=get_current_user_rank())
    return render_template("dashboard.html", next_race=None, current_user_rank=get_current_user_rank())

@app.route("/predict/<int:race_id>", methods=["GET", "POST"])
@login_required
def predict(race_id):
    race = db.get_or_404(Race, race_id)
    current_time = utc_now()
    deadline_date = prediction_deadline(race.race_date)
    
    # Check if race has started (1 hour before race)
    if current_time > deadline_date:
        flash("Prediction deadline has passed. Predictions are locked from 1 hour before the race.", "danger")
        return redirect(url_for('dashboard'))
    
    # Get existing prediction if it exists
    prediction = Prediction.query.filter_by(
        user_id=current_user.id,
        race_id=race.id
    ).first()
    
    # If prediction exists and has been evaluated, don't allow editing
    if prediction and prediction.points_earned > 0:
        flash("This race has already been evaluated. Predictions cannot be modified.", "danger")
        return redirect(url_for('dashboard'))
    
    form = PredictionForm()
    
    # Get drivers from API
    drivers = JolpiErgastAPI.get_drivers(0)  # session_key is ignored now
    driver_choices = [
        (d['permanentNumber'], f"{d.get('givenName', '')} {d.get('familyName', '')}".strip())
        for d in drivers
        if d.get('permanentNumber')
    ]
    if not driver_choices:
        flash("Driver data is currently unavailable. Please try again later.", "danger")
        return redirect(url_for('dashboard'))
    form.p1.choices = driver_choices
    form.p2.choices = driver_choices
    form.p3.choices = driver_choices
    form.last_place.choices = driver_choices
    form.dnf.choices = driver_choices
    form.fastest_lap.choices = driver_choices
    
    # Get teams from API
    teams = JolpiErgastAPI.get_team_points(0)  # session_key is ignored now
    team_choices = [
        (constructor['constructorId'], constructor.get('name', constructor['constructorId']))
        for constructor in ((team.get('Constructor') or {}) for team in teams)
        if constructor.get('constructorId')
    ]
    if not team_choices:
        flash("Team data is currently unavailable. Please try again later.", "danger")
        return redirect(url_for('dashboard'))
    form.team_podium.choices = team_choices
    form.team_most_points.choices = team_choices
    
    # If it's a GET request and we have an existing prediction, populate the form
    if request.method == 'GET' and prediction:
        form.p1.data = prediction.p1
        form.p2.data = prediction.p2
        form.p3.data = prediction.p3
        form.last_place.data = prediction.last_place
        form.dnf.data = prediction.dnf
        form.fastest_lap.data = prediction.fastest_lap
        form.team_podium.data = prediction.team_podium
        form.team_most_points.data = prediction.team_most_points
        form.safety_car.data = prediction.safety_car
        form.red_flag.data = prediction.red_flag
        form.wet_race.data = prediction.wet_race
    
    if form.validate_on_submit():
        if prediction:
            # Update existing prediction
            prediction.p1 = form.p1.data
            prediction.p2 = form.p2.data
            prediction.p3 = form.p3.data
            prediction.last_place = form.last_place.data
            prediction.dnf = form.dnf.data
            prediction.fastest_lap = form.fastest_lap.data
            prediction.team_podium = form.team_podium.data
            prediction.team_most_points = form.team_most_points.data
            prediction.safety_car = form.safety_car.data
            prediction.red_flag = form.red_flag.data
            prediction.wet_race = form.wet_race.data
            flash("Your prediction has been updated!", "success")
        else:
            # Create new prediction
            prediction = Prediction(
                user_id=current_user.id,
                race_id=race.id,
                p1=form.p1.data,
                p2=form.p2.data,
                p3=form.p3.data,
                last_place=form.last_place.data,
                dnf=form.dnf.data,
                fastest_lap=form.fastest_lap.data,
                team_podium=form.team_podium.data,
                team_most_points=form.team_most_points.data,
                safety_car=form.safety_car.data,
                red_flag=form.red_flag.data,
                wet_race=form.wet_race.data
            )
            db.session.add(prediction)
            flash("Your prediction has been saved!", "success")
        
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template("predict.html", form=form, race=race, deadline_date=deadline_date, prediction=prediction)

@app.route("/standings")
@login_required
def user_standings():
    users = User.query.order_by(User.points.desc()).all()
    return render_template("standings.html", users=users)

@app.route("/admin")
@login_required
@admin_required
def admin():
    users = User.query.all()
    races = Race.query.order_by(Race.race_date.desc()).all()
    predictions = Prediction.query.all()
    return render_template(
        "admin.html",
        users=users,
        races=races,
        predictions=predictions,
    )

@app.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    form = build_admin_form()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        db.session.commit()
        flash("User updated successfully", "success")
        return redirect(url_for('admin'))
    
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role_id
    return render_template("edit_user.html", form=form, user=user)

@app.route("/prediction/<int:prediction_id>")
@login_required
def view_prediction(prediction_id):
    prediction = db.get_or_404(Prediction, prediction_id)
    
    # Ensure user can only view their own predictions
    if prediction.user_id != current_user.id:
        flash("You can only view your own predictions.", "danger")
        return redirect(url_for('dashboard'))
    
    # Get driver names for better readability
    drivers = JolpiErgastAPI.get_drivers(0)
    driver_map = {
        d['permanentNumber']: f"{d.get('givenName', '')} {d.get('familyName', '')}".strip()
        for d in drivers
        if d.get('permanentNumber')
    }
    
    return render_template("prediction_details.html", 
                         prediction=prediction, 
                         race=prediction.race,
                         driver_map=driver_map)

@app.route('/admin/races')
@login_required
@admin_required
def admin_races():
    races = Race.query.order_by(Race.race_date.desc()).all()
    race_statuses = {race.id: get_race_status(race) for race in races}
    return render_template('admin/races.html', races=races, race_statuses=race_statuses)

@app.route('/admin/race/<int:race_id>/evaluate', methods=['GET', 'POST'])
@login_required
@admin_required
def evaluate_race(race_id):
    race = db.get_or_404(Race, race_id)
    form = FlaskForm()
    
    if request.method == 'POST':
        # Get race results from API
        current_year = utc_now().year
        race_results = JolpiErgastAPI.get_race_results(current_year, race.meeting_key)
        
        if not race_results:
            flash('Could not fetch race results from API', 'danger')
            return redirect(url_for('admin_races'))
        
        actual_results = build_actual_results(race_results)
        if not actual_results:
            flash('Race results from the API were incomplete and could not be evaluated.', 'danger')
            return redirect(url_for('admin_races'))
        
        # Get all predictions for this race
        predictions = Prediction.query.filter_by(race_id=race_id).all()
        
        for prediction in predictions:
            points = score_prediction(prediction, actual_results)
            previous_points = prediction.points_earned or 0
            prediction.points_earned = points
            prediction.user.points = (prediction.user.points or 0) + points - previous_points
        
        # Mark race as completed
        race.is_completed = True
        
        db.session.commit()
        flash('Race has been evaluated successfully!', 'success')
        return redirect(url_for('admin_races'))
    
    # For GET request, show confirmation page
    return render_template('admin/evaluate_race.html', race=race, form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
