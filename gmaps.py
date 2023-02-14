import googlemaps
from pprint import pprint
import geopy.distance

with open('google_api_key', 'r') as fh:
    API_KEY = fh.read().strip()
    fh.close()
gmaps = googlemaps.Client(key = API_KEY)

def get_places(zip_code=None, radius_miles=None, keywords=None):

    zip_code = int(zip_code) if zip_code is not None else 97116
    radius_meters_max = 50000
    if radius_miles is None:
        radius_meters = radius_meters_max
        radius_miles = get_meters_to_miles(radius_meters)
    else:
        radius_miles = float(radius_miles)
        radius_meters = get_miles_to_meters(radius_miles)
        radius_meters = radius_meters if radius_meters <= radius_meters_max else radius_meters_max
    keywords = keywords.split(',') if keywords is not None else ['pet store', 'pet grooming', 'veterinary']
    lat_lng = get_lat_lng(zip_code)

    result_ids = []
    result = {}
    for keyword in keywords:
        for res in gmaps.places_nearby(location=lat_lng, radius=radius_meters, keyword=keyword.strip())['results']:
            if res['place_id'] not in result_ids:
                result_ids.append(res['place_id'])
                dest_lat_lng = '%s,%s' % (res['geometry']['location']['lat'], res['geometry']['location']['lng'])
                distance_miles = get_distance_miles(lat_lng, dest_lat_lng)

                print('distance_miles:', distance_miles)
                print('radius_miles:', radius_miles)
                
                if round(distance_miles, 1) <= round(radius_miles, 1):
                    res['distance_miles'] = round(distance_miles, 1)
                    dict_key = '%s.%s' % (str(distance_miles).split('.')[0].rjust(5, '0'), str(distance_miles).split('.')[1].ljust(20, '0'))
                    result[dict_key] = res
    result_sorted = []
    for key in sorted(result.keys()):
        result_sorted.append(result[key])
    result = result_sorted

    print('\n#####', '\nzip_code:', zip_code, '\nradius_miles:', radius_miles, '\nkeywords:', keywords, '\n---')
    for res in result:
        print('place_id: "%s", distance_miles: "%s", name: "%s"' % (res['place_id'], res['distance_miles'], res['name']))
    print('---', '\nlen(result):', len(result), '\n#####\n')

    return result_sorted

def get_place_detail(place_id=None):
    place_detail = None
    if place_id is not None:
        place_detail = gmaps.place( place_id=place_id, fields=['place_id', 'name', 'formatted_address', 'formatted_phone_number', 'url', 'website'] )['result']
        print('\n###')
        pprint(place_detail)
    return place_detail

def get_lat_lng(zip_code):
    geo_loc = gmaps.geocode(zip_code)[0]['geometry']['location']
    return '%s,%s' % (geo_loc['lat'], geo_loc['lng'])

def get_distance_miles(origin, destination):
    return geopy.distance.geodesic(origin, destination).miles

def get_miles_to_meters(radius_miles):
    return int(float(radius_miles) * 1609.34)

def get_meters_to_miles(radius_meters):
    return int(float(radius_meters) / 1609.34)

if __name__ == "__main__":
    get_places()
