import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
from config import Config


class JolpiErgastAPI:
    BASE_URL = Config.JOLPI_ERGAST_API_BASE_URL

    @staticmethod
    def _get_json(url: str):
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_race_results(season, round_number):
        """Fetch race results for a specific race."""
        url = f"{JolpiErgastAPI.BASE_URL}/{season}/{round_number}/results.json"
        try:
            data = JolpiErgastAPI._get_json(url)
            races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            if races:
                return races[0]
        except requests.RequestException:
            return None
        return None

    @staticmethod
    def get_next_race() -> Optional[Dict]:
        """Get the next upcoming race."""
        current_year = datetime.now(timezone.utc).year
        url = f"{JolpiErgastAPI.BASE_URL}/{current_year}/next.json"
        try:
            data = JolpiErgastAPI._get_json(url)
            races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            if races:
                race = races[0]
                return {
                    'meeting_key': int(race['round']),
                    'meeting_name': race.get('raceName', 'Unknown Race'),
                    'date_start': f"{race['date']}T{race.get('time', '00:00:00Z')}"
                }
        except requests.RequestException:
            return None
        return None
    
    @staticmethod
    def get_drivers(session_key: int) -> List[Dict]:
        """Get list of drivers."""
        current_year = datetime.now(timezone.utc).year
        url = f"{JolpiErgastAPI.BASE_URL}/{current_year}/drivers.json"
        try:
            data = JolpiErgastAPI._get_json(url)
            return data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        except requests.RequestException:
            return []
        return []
    
    @staticmethod
    def get_team_points(session_key: int) -> List[Dict]:
        """Get team points."""
        current_year = datetime.now(timezone.utc).year
        url = f"{JolpiErgastAPI.BASE_URL}/{current_year}/constructorStandings.json"
        try:
            data = JolpiErgastAPI._get_json(url)
            standings = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
            if standings:
                return standings[0].get('ConstructorStandings', [])
        except requests.RequestException:
            return []
        return []
