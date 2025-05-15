import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging
from flask_app.models import RaceSchedule
from flask_app import db

class OpenF1API:
    BASE_URL = "https://api.jolpi.ca/ergast/f1"
    
    @staticmethod
    def get_race_results(season, round_number):
        """Fetch race results for a specific race."""
        url = f"{OpenF1API.BASE_URL}/{season}/{round_number}/results.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['MRData']['RaceTable']['Races']:
                return data['MRData']['RaceTable']['Races'][0]
        return None

    @staticmethod
    def get_next_race() -> Optional[Dict]:
        """Get the next upcoming race."""
        current_year = datetime.now().year
        url = f"{OpenF1API.BASE_URL}/{current_year}/next.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['MRData']['RaceTable']['Races']:
                race = data['MRData']['RaceTable']['Races'][0]
                return {
                    'meeting_key': race['round'],
                    'meeting_name': race['raceName'],
                    'date_start': f"{race['date']}T{race['time']}"
                }
        return None
    
    @staticmethod
    def get_drivers(session_key: int) -> List[Dict]:
        """Get list of drivers."""
        current_year = datetime.now().year
        url = f"{OpenF1API.BASE_URL}/{current_year}/drivers.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['MRData']['DriverTable']['Drivers']
        return []
    
    @staticmethod
    def get_team_points(session_key: int) -> List[Dict]:
        """Get team points."""
        current_year = datetime.now().year
        url = f"{OpenF1API.BASE_URL}/{current_year}/constructorStandings.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
        return [] 