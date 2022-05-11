from geopy.geocoders import Nominatim, options
from geopy.exc import GeopyError

# Geolocation agent being used
options.default_timeout = 5 # Seconds to wait before timeout
geolocator = Nominatim(user_agent="aparkapp")
# Returns JSON or Point with coordinates given an address
# <param>raw</query> Determines if a JSON or just its point"
def address_to_coordinates(query, county_code="ES", only_one_result=True, raw=True):
    res=None
    try:
        geolocation=geolocator.geocode(query=query, country_codes=county_code, exactly_one=only_one_result)
        res=[geolocation.address,[geolocation.latitude, geolocation.longitude]]   
    except GeopyError:
        res=False
    return res
    
# Returns address given a tuple with coordinates
# <param>query</query> (37.21,92.0) or "%(37.21)s,%(92.0)s"
def coordinates_to_address(query, only_one_result=True):
    res=None
    try:
        geolocation=geolocator.reverse(query=query, exactly_one=only_one_result)
        res=[geolocation.address,[geolocation.latitude, geolocation.longitude]]
    except GeopyError:
        res=False
    return res
