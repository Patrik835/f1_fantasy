from datetime import timedelta

import pytest

from flask_app import app as flask_app, db, seed_default_roles
from flask_app.models import Prediction, Race, Role, User
from flask_app.time_utils import to_utc_naive, utc_now
import flask_app.routes as routes


@pytest.fixture(scope="session", autouse=True)
def configure_app(tmp_path_factory):
    database_path = tmp_path_factory.mktemp("data") / "test.db"
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
    )


@pytest.fixture
def client():
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        seed_default_roles()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def api_mocks(monkeypatch):
    next_race_date = utc_now() + timedelta(days=7)

    monkeypatch.setattr(
        routes.JolpiErgastAPI,
        "get_next_race",
        staticmethod(lambda: {
            "meeting_key": 1,
            "meeting_name": "Test Grand Prix",
            "date_start": next_race_date.isoformat().replace("+00:00", "Z"),
        }),
    )
    monkeypatch.setattr(
        routes.JolpiErgastAPI,
        "get_drivers",
        staticmethod(lambda session_key: [
            {"permanentNumber": "44", "givenName": "Lewis", "familyName": "Hamilton"},
            {"permanentNumber": "1", "givenName": "Max", "familyName": "Verstappen"},
            {"permanentNumber": "16", "givenName": "Charles", "familyName": "Leclerc"},
        ]),
    )
    monkeypatch.setattr(
        routes.JolpiErgastAPI,
        "get_team_points",
        staticmethod(lambda session_key: [
            {"Constructor": {"constructorId": "mercedes", "name": "Mercedes"}},
            {"Constructor": {"constructorId": "red_bull", "name": "Red Bull"}},
            {"Constructor": {"constructorId": "ferrari", "name": "Ferrari"}},
        ]),
    )


def create_user(username="user", role_name="user"):
    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=f"{username}@example.com", role=role)
    user.password = "secret"
    db.session.add(user)
    db.session.commit()
    return user


def login(client, username="user", password="secret"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def prediction_payload(p1="44"):
    return {
        "p1": p1,
        "p2": "1",
        "p3": "16",
        "last_place": "16",
        "dnf": "16",
        "fastest_lap": "44",
        "team_podium": "mercedes",
        "team_most_points": "mercedes",
        "safety_car": "no",
        "red_flag": "no",
        "wet_race": "no",
    }


def test_register_login_and_dashboard(client, api_mocks):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "secret",
            "repeatpassword": "secret",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert User.query.filter_by(username="newuser").first() is not None

    response = login(client, "newuser")
    assert response.status_code == 200
    assert b"Next Race: Test Grand Prix" in response.data
    assert Race.query.filter_by(meeting_key=1).first() is not None


def test_prediction_create_and_update(client, api_mocks):
    create_user()
    login(client)
    client.get("/dashboard")
    race = Race.query.filter_by(meeting_key=1).one()

    response = client.post(f"/predict/{race.id}", data=prediction_payload(), follow_redirects=True)
    assert response.status_code == 200
    prediction = Prediction.query.filter_by(race_id=race.id).one()
    assert prediction.p1 == "44"

    response = client.post(f"/predict/{race.id}", data=prediction_payload(p1="1"), follow_redirects=True)
    assert response.status_code == 200
    assert Prediction.query.filter_by(race_id=race.id).one().p1 == "1"


def test_admin_access_and_race_management(client, api_mocks):
    create_user()
    create_user("admin", "admin")
    race = Race(
        meeting_key=2,
        race_name="Finished Grand Prix",
        race_date=to_utc_naive(utc_now() - timedelta(days=1)),
    )
    db.session.add(race)
    db.session.commit()

    login(client)
    response = client.get("/admin", follow_redirects=True)
    assert b"You do not have permission" in response.data

    login(client, "admin")
    assert client.get("/admin").status_code == 200
    response = client.get("/admin/races")
    assert response.status_code == 200
    assert b"Evaluate Race" in response.data


def test_race_evaluation_is_resilient_and_idempotent(client, monkeypatch):
    admin = create_user("admin", "admin")
    user = create_user()
    race = Race(
        meeting_key=3,
        race_name="Evaluated Grand Prix",
        race_date=to_utc_naive(utc_now() - timedelta(days=1)),
    )
    db.session.add(race)
    db.session.commit()
    prediction = Prediction(user_id=user.id, race_id=race.id, **prediction_payload())
    db.session.add(prediction)
    db.session.commit()

    monkeypatch.setattr(
        routes.JolpiErgastAPI,
        "get_race_results",
        staticmethod(lambda season, round_number: {
            "Results": [
                {
                    "Driver": {"permanentNumber": "44"},
                    "Constructor": {"constructorId": "mercedes"},
                    "points": "25",
                    "status": "Finished",
                    "positionText": "1",
                    "FastestLap": {"rank": "1"},
                },
                {
                    "Driver": {"permanentNumber": "1"},
                    "Constructor": {"constructorId": "red_bull"},
                    "points": "18",
                    "status": "Finished",
                    "positionText": "2",
                },
                {
                    "Driver": {"permanentNumber": "16"},
                    "Constructor": {"constructorId": "ferrari"},
                    "status": "Accident",
                    "positionText": "R",
                },
            ]
        }),
    )

    login(client, admin.username)
    response = client.post(f"/admin/race/{race.id}/evaluate", follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Prediction, prediction.id).points_earned == 22
    assert db.session.get(User, user.id).points == 22
    assert db.session.get(Race, race.id).is_completed is True

    client.post(f"/admin/race/{race.id}/evaluate", follow_redirects=True)
    assert db.session.get(User, user.id).points == 22
