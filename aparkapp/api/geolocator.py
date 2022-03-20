from geopy.geocoders import Nominatim 

#Geolocation 
geolocator = Nominatim(user_agent="AparkApp")
# Returns JSON or Point with coordinates given an address
# <param>raw</query> Determines if a JSON or just its point"
def address_to_coordinates(query, county_code="ES", only_one_result=False, raw=True):
    locations = []
    try:
        res=geolocator.geocode(query=query, country_codes=county_code, exactly_one=only_one_result)
        if hasattr(res, 'raw') and raw:
            locations=[loc for loc in res]
        elif hasattr(res, 'point'):
           locations=[loc.point for loc in res] 
        else:
           locations=[loc for loc in res]  
    except:
        raise ValueError
    return locations
    
# Returns address given a tuple with coordinates
# <param>query</query> (37.21,92.0) or "%(37.21)s,%(92.0)s"
def coordinates_to_address(query, only_one_result=False):
    try:
        res=geolocator.reverse(query=query, exactly_one=only_one_result)
        if hasattr(res, 'raw'):
            response=[loc.raw for loc in res]
        else:
            response=[loc for loc in res]
    except:
        raise ValueError
    return response
