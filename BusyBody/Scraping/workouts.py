import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(total=5, backoff_factor=20, status_forcelist=[429])
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)

BASE_URL = 'https://www.muscleandstrength.com'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

MAX_THREADS = 30


def getWorkoutTypes() -> [dict]:
    """
    :return: List of dictionaries containing workout type name and URL for its routines
    """
    response = session.get(f'{BASE_URL}/workout-routines', headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = list()
    types_div = soup.find('div', class_='mainpage-category-list')
    all_types = types_div.findAll('div', class_='cell')
    for t in all_types:
        data.append({
            'url': f'{BASE_URL}{t.a["href"]}',
            'type_name': t.div.text
        })
    return data


def getRoutines(workout_type, item_list) -> [dict]:
    response = session.get(workout_type['url'], headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    workout_routine = soup.findAll('div', class_='bp600-6')
    for routine in workout_routine:
        div_info = routine.find('div', class_='node-title')
        div_desc = routine.find('div', class_='node-short-summary')
        item_list.append({
            'url': f'{BASE_URL}{div_info.a["href"]}',
            'routine_title': div_info.a.text.strip(),
            'routine_desc': div_desc.text.strip(),
            'category': workout_type['type_name']
        })


def getWorkoutInfo(routine, item_list) -> [dict]:
    response = session.get(routine['url'], headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    summary = soup.find('div', class_='node-stats-block')
    goal = summary.find('div', class_='field-name-field-main-goal').text.strip()
    training_level = summary.find('div', class_='field-name-field-experience-level').text.strip()
    days_per_week = summary.find('div', class_='field-name-field-days-per-week').text.strip()
    prog_duration = summary.ul.contents[7].contents[1]
    time_per_workout = summary.ul.contents[11].contents[1]
    equipment = summary.ul.contents[13].contents[1].text

    item_list.append({
        'goal': goal,
        'training_level': training_level,
        'days_per_week': days_per_week,
        'program_duration': prog_duration,
        'time_per_workout': time_per_workout,
        'equipment': equipment,
        'url': routine['url'],
        'name': routine['routine_title'],
        'description': routine['routine_desc'],
        'category': routine['category']
    })


if __name__ == "__main__":
    workout_types = getWorkoutTypes()
    routines = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_routines = {executor.submit(getRoutines, t, routines) for t in workout_types}
        for future in concurrent.futures.as_completed(future_to_routines):
            try:
                future.result()
            except Exception as e:
                print(f" generated Exception in ROUTINES {e}")

    workout_info_list = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_workouts = {executor.submit(getWorkoutInfo, r, workout_info_list) for r in routines}
        for future in concurrent.futures.as_completed(future_to_workouts):
            try:
                future.result()
            except Exception as e:
                print(f" generated Exception in WORKOUT INFO {e}")

    with open('../Data/workouts.json', 'w') as f_out:
        json.dump(workout_info_list, f_out, indent=4)
