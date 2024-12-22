import math

def haversine(lat1, lon1, lat2, lon2, office_radius=5):
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius_earth_km = 6371  # Radius of the Earth in kilometers
    distance_km = radius_earth_km * c
    
    return distance_km < office_radius


def to_float_or_0(val):
    try:
        return float(val)
    except:
        return 0