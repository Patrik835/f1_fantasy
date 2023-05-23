import requests
from datetime import datetime, date

# class Fetched_answers:

def get_number_of_the_race():
    race_nr = 0
    qualifying_dates = {}
    current_date = datetime.now().date()
    response = requests.get('http://ergast.com/api/f1/current.json')
    data = response.json()
    races = data['MRData']['RaceTable']['Races']

    for race in races:
        race_name = race['raceName']
        race_d = race['Qualifying']['date']
        race_date = datetime.strptime(race_d, '%Y-%m-%d').date()
        qualifying_dates[race_name]=race_date
    for race_name, race_date in qualifying_dates.items():
        race_nr += 1
        if race_date > current_date:
            next_race = race_name
            break
    return next_race, race_nr

# print(get_number_of_the_race())
def get_drivers_positions():
    dnf = []
    colided = []
    memory = 0
    next_race_name, race_number = get_number_of_the_race()
    response = requests.get(f'http://ergast.com/api/f1/2023/{str(race_number-1)}/results.json')
    data = response.json()
    result_table = data['MRData']['RaceTable']['Races'][0]['Results']
    for result in result_table:
        if result["position"] == '1':
            p_1 = [result["Driver"]["code"],result["Constructor"]["constructorId"]]
        elif result["position"] == '2':
            p_2 = [result["Driver"]["code"],result["Constructor"]["constructorId"]]
        elif result["position"] == '3':
            p_3 = [result["Driver"]["code"], result["Constructor"]["constructorId"]]
        if result['status'] != 'Finished':
            dnf.append(result["Driver"]["code"])
        elif result['status'] == 'Finished':
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
    return p_1, p_2, p_3, dnf, p_last, fastest_lap, fastest_lap_lap, collision
# print(get_drivers_positions())

def get_qual_positions ():
    next_race_name, race_number = get_number_of_the_race()
    response = requests.get(f'https://ergast.com/api/f1/2023/{race_number-1}/qualifying.json')
    data = response.json()
    result_table = data['MRData']['RaceTable']['Races'][0]["QualifyingResults"]
    for result in result_table:
        if result["position"] == '1':
            qual_1 = [result["Driver"]["code"],result["Constructor"]["constructorId"]]
    return qual_1
# print(get_qual_positions())

def append_to_answers_list():
    answers_list = [0,0,0,0,0,0,0,0,0,0,0,0]
    p_1, p_2, p_3, dnf, p_last, fastest_lap, fastest_lap_lap , collision = get_drivers_positions()
    qual_1 = get_qual_positions()
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
    if qual_1[1] == p_1[1]:
        answers_list[8] = 'yes'
    else:
        answers_list[8] = 'no'
    answers_list[2] = fastest_lap
    answers_list[3] = p_last
    answers_list[4] = dnf
    answers_list[5] = collision
    answers_list[11] = fastest_lap_lap
    
    return answers_list
print(append_to_answers_list())
