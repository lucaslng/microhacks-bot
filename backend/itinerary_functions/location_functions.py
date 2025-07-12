import requests
from util.apikeys import gmaps_key


def get_restauraunts(place_id: str, radius: int) -> list:
  """Finds the restauraunts nearby a given location with a place_id.

  Args:
      place_id: The google maps place_id of the location to find restauraunts around, e.g. ChIJiQHsW0m3j4ARm69rRkrUF3w
      radius: The radius to search for restauraunts around the area in meters, e.g. 200

  Returns:
      A list containing the google maps place_ids of all the restauraunts found.
  """

  headers = {
    'X-Goog-Api-Key': gmaps_key,
    'Content-Type': 'application/json',
  }

  json_data = {
      "insights": [
          "INSIGHT_PLACES",
      ],
      "filter": {
          "locationFilter": {
              "circle": {
                  "place": f"places/{place_id}",
                  "radius": radius
              }
          },
          "typeFilter": {
              "includedTypes": [
                  "restaurant"
              ]
          },
          "operatingStatus": [
              "OPERATING_STATUS_OPERATIONAL",
              "OPERATING_STATUS_TEMPORARILY_CLOSED"
          ],
          "ratingFilter": {
              "minRating": 4.0,
              "maxRating": 5
          }
      }
  }

  response = requests.post(
    'https://areainsights.googleapis.com/v1:computeInsights', headers=headers, json=json_data)
  data: dict[str, str] = response.json()["placeInsights"][0]
  print("Called get_restauraunts function:", data)
  return [v.removeprefix("places/") for _, v in data]


def get_place(place_id: str) -> dict:
  """Gets the information of a place using a google maps place_id.

  Args:
      place_id: The google maps place_id of the location to get information on, e.g. ChIJiQHsW0m3j4ARm69rRkrUF3w

  Returns:
      A dictionary containing the name, address of the location as well as information about things nearby. 
  """

  headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': gmaps_key,
    'X-Goog-FieldMask': 'displayName,formattedAddress,addressDescriptor',
      }

  response = requests.get(
      f'https://places.googleapis.com/v1/places/{place_id}', headers=headers)
  print("Called get_place function:", response.text)
  return response.json()
