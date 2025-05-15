from flask import render_template, flash, redirect, url_for, session, request
from flask_app.models import User, Role, Race, Prediction
from flask_app.forms import LoginForm, RegisterForm, PredictionForm, AdminUserForm
from flask_app.api_service import OpenF1API
from flask_app import app, db
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta, timezone
from functools import wraps

csrf = CSRFProtect(app)

# Flask login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    next_race = OpenF1API.get_next_race()
    if next_race:
        race_date = datetime.fromisoformat(next_race['date_start'].replace('Z', '+00:00'))
        # Ensure race_date is timezone-aware (UTC)
        if race_date.tzinfo is None or race_date.tzinfo.utcoffset(race_date) is None:
            race_date = race_date.replace(tzinfo=timezone.utc)
        else:
            race_date = race_date.astimezone(timezone.utc)
        # Set deadline to one hour before race start
        deadline_date = race_date - timedelta(hours=1)
        current_date = datetime.now(timezone.utc)
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
    next_race = OpenF1API.get_next_race()
    if next_race:
        race_date = datetime.fromisoformat(next_race['date_start'].replace('Z', '+00:00'))
        deadline_date = race_date - timedelta(hours=1)
        
        # Get user's prediction for next race if exists
        race = Race.query.filter_by(meeting_key=next_race['meeting_key']).first()
        if not race:
            race = Race(
                meeting_key=next_race['meeting_key'],
                race_name=next_race['meeting_name'],
                race_date=race_date
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
                             prediction=prediction)
    return render_template("dashboard.html", next_race=None)

@app.route("/predict/<int:race_id>", methods=["GET", "POST"])
@login_required
def predict(race_id):
    race = Race.query.get_or_404(race_id)
    current_time = datetime.now(timezone.utc)
    
    # Ensure race date is timezone-aware
    if race.race_date.tzinfo is None:
        race.race_date = race.race_date.replace(tzinfo=timezone.utc)
    
    # Check if race has started (1 hour before race)
    if current_time > race.race_date - timedelta(hours=1):
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
    drivers = OpenF1API.get_drivers(0)  # session_key is ignored now
    driver_choices = [(d['permanentNumber'], f"{d['givenName']} {d['familyName']}") for d in drivers]
    form.p1.choices = driver_choices
    form.p2.choices = driver_choices
    form.p3.choices = driver_choices
    form.last_place.choices = driver_choices
    form.dnf.choices = driver_choices
    form.fastest_lap.choices = driver_choices
    
    # Get teams from API
    teams = OpenF1API.get_team_points(0)  # session_key is ignored now
    team_choices = [(t['Constructor']['constructorId'], t['Constructor']['name']) for t in teams]
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
    
    # Calculate deadline (1 hour before race)
    deadline_date = race.race_date - timedelta(hours=1)
    
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
    roles = Role.query.all()
    form = AdminUserForm()
    return render_template("admin.html", users=users, roles=roles, form=form)

@app.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm()
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]
    
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

@app.route("/admin/evaluate/<int:race_id>")
@login_required
@admin_required
def evaluate_predictions(race_id):
    race = Race.query.get_or_404(race_id)
    if not race.is_completed:
        flash("Race is not completed yet", "danger")
        return redirect(url_for('admin'))
    
    predictions = Prediction.query.filter_by(race_id=race.id).all()
    results = OpenF1API.get_race_results(0)
    
    for prediction in predictions:
        points = 0
        # Evaluate predictions and calculate points
        # (Implementation depends on your scoring system)
        
        prediction.points_earned = points
        user = User.query.get(prediction.user_id)
        user.points += points
    
    db.session.commit()
    flash("Predictions evaluated successfully", "success")
    return redirect(url_for('admin'))

@app.route("/prediction/<int:prediction_id>")
@login_required
def view_prediction(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)
    
    # Ensure user can only view their own predictions
    if prediction.user_id != current_user.id:
        flash("You can only view your own predictions.", "danger")
        return redirect(url_for('dashboard'))
    
    # Get driver names for better readability
    drivers = OpenF1API.get_drivers(0)
    driver_map = {d['permanentNumber']: f"{d['givenName']} {d['familyName']}" for d in drivers}
    
    return render_template("prediction_details.html", 
                         prediction=prediction, 
                         race=prediction.race,
                         driver_map=driver_map)

@app.route('/admin/races')
@login_required
@admin_required
def admin_races():
    races = Race.query.order_by(Race.race_date.desc()).all()
    now = datetime.now(timezone.utc)
    
    # Ensure all race dates are timezone-aware
    for race in races:
        if race.race_date.tzinfo is None:
            race.race_date = race.race_date.replace(tzinfo=timezone.utc)
    
    print(f"Admin races route called. Found {len(races)} races:")
    for race in races:
        print(f"- {race.race_name} ({race.race_date})")
    return render_template('admin/races.html', races=races, now=now)

@app.route('/admin/race/<int:race_id>/evaluate', methods=['GET', 'POST'])
@login_required
@admin_required
def evaluate_race(race_id):
    race = Race.query.get_or_404(race_id)
    form = AdminUserForm()  # Create a form instance for CSRF protection
    
    if request.method == 'POST':
        # Get race results from API
        current_year = datetime.now().year
        race_results = OpenF1API.get_race_results(current_year, race.meeting_key)
        
        if not race_results:
            flash('Could not fetch race results from API', 'danger')
            return redirect(url_for('admin_races'))
        
        # Extract actual results from API data
        results = race_results['Results']
        actual_results = {
            'p1': results[0]['Driver']['permanentNumber'],
            'p2': results[1]['Driver']['permanentNumber'],
            'p3': results[2]['Driver']['permanentNumber'],
            'last_place': results[-1]['Driver']['permanentNumber'],
            'dnf': next((r['Driver']['permanentNumber'] for r in results if r['status'] != 'Finished'), None),
            'fastest_lap': next((r['Driver']['permanentNumber'] for r in results if r.get('FastestLap', {}).get('rank') == '1'), None),
            'team_podium': results[0]['Constructor']['constructorId'],
            'team_most_points': max(
                (team for team in results),
                key=lambda x: int(x['points'])
            )['Constructor']['constructorId'],
            'safety_car': 'yes' if any(r.get('status') == 'Safety Car' for r in results) else 'no',
            'red_flag': 'yes' if any(r.get('status') == 'Red Flag' for r in results) else 'no',
            'wet_race': 'yes' if any(r.get('status') == 'Wet Race' for r in results) else 'no'
        }
        
        # Get all predictions for this race
        predictions = Prediction.query.filter_by(race_id=race_id).all()
        
        for prediction in predictions:
            points = 0
            
            # Check podium positions (3 points each)
            if prediction.p1 == actual_results['p1']:
                points += 3
            if prediction.p2 == actual_results['p2']:
                points += 3
            if prediction.p3 == actual_results['p3']:
                points += 3
                
            # Check last place (2 points)
            if prediction.last_place == actual_results['last_place']:
                points += 2
                
            # Check DNF (2 points)
            if prediction.dnf == actual_results['dnf']:
                points += 2
                
            # Check fastest lap (2 points)
            if prediction.fastest_lap == actual_results['fastest_lap']:
                points += 2
                
            # Check team predictions (2 points each)
            if prediction.team_podium == actual_results['team_podium']:
                points += 2
            if prediction.team_most_points == actual_results['team_most_points']:
                points += 2
                
            # Check race conditions (1 point each)
            if prediction.safety_car == actual_results['safety_car']:
                points += 1
            if prediction.red_flag == actual_results['red_flag']:
                points += 1
            if prediction.wet_race == actual_results['wet_race']:
                points += 1
            
            # Update prediction points
            prediction.points_earned = points
            
            # Update user's total points
            user = prediction.user
            user.points += points
        
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