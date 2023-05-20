import requests
from utils.utils import dump_json

API_KEY = 'hDJA3ouPtWChXPAlohees9VhLIv2s6iZEhCyXuEfDabG5sQtaM26h71jCrYbG_gHV1VMySuI7c34j7lmfq' \
          '-EA4LJs__Pi3WFI1ME2KCDaBU-a66KogMd5XBKHgoVYHYx'

PARAMS = {
    # 'location': 'Irvine, California',
    'term': 'restaurants',
    'sort_by': 'best_match',
    'limit': 50
}

HEADER = {
    "accept": "application/json",
    'Authorization': f'Bearer {API_KEY}'
}

ENDPOINT = 'https://api.yelp.com/v3/businesses/search'

# top: 33.734440, -117.848005
# bottom: 33.629878, -117.683554
# right: 33.586130, -117.832899
# left: 33.654173, -117.984648
# laguna: 33.592994, -117.715826
# costco huntington: 33.737295, -117.990484
COORDINATES = [
    [33.734440, -117.848005],
    [33.629878, -117.683554],
    [33.586130, -117.832899],
    [33.654173, -117.984648],
    [33.592994, -117.715826],
    [33.737295, -117.990484]
]  # c[0] = latitude, c[1] = longitude


if __name__ == "__main__":
    full_data = list()
    seen_ids = set()

    try:
        for c in COORDINATES:
            lat, long = c[0], c[1]
            print(f"Collecting data for latitude: {lat} and longitude: {long}")
            PARAMS['latitude'], PARAMS['longitude'] = lat, long
            r = requests.get(url=ENDPOINT, params=PARAMS, headers=HEADER)
            results = r.json()['businesses']
            print(f"{len(results)} total results collected")

            for res in results:
                if res['id'] not in seen_ids:
                    full_data.append(res)
                seen_ids.add(res['id'])

    except KeyError as e:
        print(f"Error encountered from Yelp API response: {e}")

    dump_json('../Data/yelp.json', full_data)
    # Result: 252 unique restaurants
