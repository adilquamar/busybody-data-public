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

BASE_URL = 'https://eatthegains.com/macro-friendly-recipes/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

MAX_THREADS = 30


def getRecipeLinks() -> [dict]:
    response = session.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = list()
    for p in soup.findAll('p'):
        for a in p.findAll('a'):
            if a.find('strong') and a.get('href'):
                recipe_info = {
                    'url': a['href'],
                    'title': a.text.strip(),
                    'desc': p.text.strip()
                }
                data.append(recipe_info)
    return data


def getMacros(url: str) -> dict:
    response = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    macros = soup.findAll('div', class_='wprm-recipe-nutrition-container')
    macro_info = dict()
    for macro in macros:
        name = macro.find('span', class_='wprm-recipe-nutrition-label')
        values_info = macro.find('span', class_='wprm-recipe-nutrition-with-unit').contents
        macro_type = name.text[0:-2].lower()  # string to represent key in macro info dict
        macro_value = f'{values_info[0].text}{values_info[1].text}'  # string with value and unit
        macro_info[macro_type] = macro_value
    return macro_info


def updateRecipeInfo(recipe_info: dict):
    macro_info = getMacros(recipe_info['url'])
    recipe_info.update(macro_info)


if __name__ == "__main__":
    recipe_links = getRecipeLinks()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_recipe_info = {executor.submit(updateRecipeInfo, info) for info in recipe_links}
        for future in concurrent.futures.as_completed(future_to_recipe_info):
            try:
                future.result()
            except Exception as e:
                print(f" generated Exception {e}")

    print(f"Collected {len(recipe_links)} recipes")

    with open('../Data/recipes.json', 'w') as f_out:
        json.dump(recipe_links, f_out, indent=4)
