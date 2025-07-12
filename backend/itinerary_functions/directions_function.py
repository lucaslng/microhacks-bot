import googlemaps
from util.apikeys import gmaps_key

gmaps = googlemaps.Client(key=gmaps_key)
print(gmaps.directions("Sydney", "Melbourne", mode="transit")) # type: ignore

def get_directions(destination: str, origin: str) -> int:
    """Gets the directions information from one location to another via transit.

    Args:
        destination: The destination location

    Returns:
        A number containing the temperature in Celsius.
    """
    # ... (implementation) ...
    
    return gmaps.directions(destination, origin, mode="transit")