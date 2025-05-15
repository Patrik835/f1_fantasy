# F1 Fantasy League

A web application for F1 Fantasy League predictions and scoring.

## Features

- User registration and authentication
- Race predictions for upcoming F1 races
- Automatic race evaluation using the OpenF1 API
- Points calculation and standings
- Admin dashboard for race management

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/f1_fantasy.git
cd f1_fantasy
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and set your configuration values.

5. Initialize the database:
```bash
flask db upgrade
```

## Running the Application

### Development
```bash
flask run
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "flask_app:create_app()"
```

## Project Structure

```
f1_fantasy/
├── flask_app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── api_service.py
│   └── templates/
├── migrations/
├── instance/
├── .env.example
├── config.py
├── requirements.txt
└── README.md
```

## API Integration

The application uses the OpenF1 API (via jolpi.ca proxy) to fetch:
- Race schedules
- Driver information
- Team standings
- Race results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# F1 Fantasy Fullstack Project
#### Formula one fantasy game with evaluation from api.
Created with Python flask app with SQLite db getting information from https://documenter.getpostman.com/view/11586746/SztEa7bL#intro api.

##### To run the app install all the requirements and run: python3/python app.py .

### Rules
- This is a formula Fantasy game where players predict the race results by answering the questions
- User can submit filled qiuz for the next race from monday after last race till the saturday 23:59 before the next race. On the race day is the form locked.
- It is possible to update the form by filling it again. As many times as you want.
- After race the quiz is evaluated and points are given
- Answers are evaluated after the race at 23:00
- Users can check their points and ranking and quiz history as well
- The winner is the one with most points at the end of the formula 1 season :bomb:
#### Have Fun and Good Luck! :rocket:

All the rules to play the game are in "rules" path as well.

