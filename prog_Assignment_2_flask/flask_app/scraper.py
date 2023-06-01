import requests
from datetime import datetime, timedelta


def get_number_of_the_race():
    race_nr = 0
    qualifying_dates = {}
    try:
        current_date = datetime.now().date()
        response = requests.get('http://ergast.com/api/f1/current.json')
        data = response.json()
        races = data['MRData']['RaceTable']['Races']
        for race in races:
            race_name = race['raceName']
            race_d = race['Qualifying']['date']
            race_date = datetime.strptime(race_d, '%Y-%m-%d').date()
            race_date += timedelta(days=1)
            qualifying_dates[race_name]=race_date
        for race_name, race_date in qualifying_dates.items():
            race_nr += 1
            if race_date >= current_date:
                next_race = race_name
                break
        return next_race, race_nr, race_date
    except:
        None, None, None
# print(get_number_of_the_race())
def get_drivers_positions():
    dnf = []
    colided = []
    memory = 0
    try:    
        next_race_name, race_number,race_date = get_number_of_the_race()
        response = requests.get(f'http://ergast.com/api/f1/2023/{str(race_number-1)}/results.json')
        data = response.json()
        result_table = data['MRData']['RaceTable']['Races'][0]['Results']
        for result in result_table:
            if result["position"] == '1':
                p_1 = [result["Driver"]["code"],result["Constructor"]["constructorId"]]
                if result['grid'] == '1':
                    pol_p1 = 'yes'
                else:
                    pol_p1 = 'no'
            elif result["position"] == '2':
                p_2 = [result["Driver"]["code"],result["Constructor"]["constructorId"]]
            elif result["position"] == '3':
                p_3 = [result["Driver"]["code"], result["Constructor"]["constructorId"]]
            if result['Driver']['driverId'] == 'norris':
                if result['points'] == '0':
                    norris_points = 'no'
                elif result['points'] > '0':
                    norris_points = 'yes'
            if result['status'] != 'Finished' and result['status'] != '+1 Lap' and result['status'] != '+2 Laps':
                dnf.append(result["Driver"]["code"])
            elif result['status'] == 'Finished' or result['status'] == '+1 Lap' or result['status'] == '+2 Laps':
                if int(result['position']) > memory:
                    p_last = result["Driver"]["code"]
                memory = int(result['position'])
            elif result['status'] == 'collision':
                colided.append(result["Driver"]["code"])
            try:
                if result['FastestLap']['rank'] == '1':
                    fastest_lap = result["Driver"]["code"]
                    fastest_lap_lap = result['FastestLap']['lap']
            except:
                KeyError
        if len(colided)>=2:
            collision = 'yes'
        else:
            collision = 'no'
        return p_1, p_2, p_3, dnf, p_last, fastest_lap, fastest_lap_lap, collision, pol_p1, norris_points
    except:
        return  None, None, None, None, None, None, None, None, None, None
# print(get_drivers_positions())


def get_construct_standings():
    try:    
        next_race_name, race_number, race_date = get_number_of_the_race()
        response = requests.get(f'https://ergast.com/api/f1/2023/{race_number-1}/constructorStandings.json',verify=False)
        data = response.json()
        result_table = data['MRData']['StandingsTable']['StandingsLists'][0]["ConstructorStandings"]
        for result in result_table:
            if result["position"] == '1':
                c_1 = result["Constructor"]["constructorId"]
        return c_1
    except:
        return None
# print(get_construct_standings())
    

def answers_list():
    try:
        answers_list = [0,0,0,0,0,0,0,0,0,0,0,0] 
        p_1, p_2, p_3, dnf, p_last, fastest_lap, fastest_lap_lap , collision, pol_p1, norris_points = get_drivers_positions()
        c_1 = get_construct_standings()
        answers_list[0] = p_1[0]
        answers_list[1] = p_2[0]
        if p_1[1] == p_2[1]:
            answers_list[9] = p_1[1]
        elif p_1[1] == p_3[1]:
            answers_list[9] = p_1[1]
        elif p_2[1] == p_3[1]:
            answers_list[9] = p_2[1]
        else:
            answers_list[9] = 'no'
        answers_list[2] = p_3[0]
        answers_list[3] = p_last
        answers_list[4] = dnf
        answers_list[5] = fastest_lap
        answers_list[6] = collision
        answers_list[7] = norris_points
        answers_list[8] = pol_p1
        answers_list[10] = c_1
        answers_list[11] = fastest_lap_lap
        return answers_list
    except:
        return None
# print(answers_list())