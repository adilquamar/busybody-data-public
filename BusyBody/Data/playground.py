from utils.utils import *


if __name__ == "__main__":
    yelp_data_list = load_json('yelp.json')
    refined_yelp_data = list()
    for yelpData in yelp_data_list:

        refined_yelp_data.append({
            'name': yelpData['name'],
            'image_url': yelpData['image_url'],
            'url': yelpData['url'],
            'rating': yelpData['rating'],
            'coordinates': yelpData['coordinates'],
            'price_level': yelpData['price'] if 'price' in yelpData.keys() else None,
            'address': yelpData['location']['display_address'],
            'phone': yelpData['display_phone']
        })
    dump_json(path='yelpSimple.json', data=refined_yelp_data)
