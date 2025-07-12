import requests
from util.apikeys import gmaps_key

api_url = 'https://maps.googleapis.com/maps/api/geocode/'

def get_place_id(location: str):
	response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?key={gmaps_key}&address={location}&language=en")
	data = response.json()
	return data["results"][0]["place_id"]