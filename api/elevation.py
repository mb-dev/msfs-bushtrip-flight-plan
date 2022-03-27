import json
import urllib
from cachier import cachier
import google_api_key


@cachier()
def get_elevation(lat, lon):
    print(f"request elevation {lat} {lon}")
    response = urllib.request.urlopen(f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat}%2C{lon}&key={google_api_key.key}")
    if response.getcode() == 200:
        data = json.loads(response.read())
        elevation = data["results"][0]["elevation"]
        return {
            "meter": elevation,
            "feet": elevation * 3.28084,
        }
    return None