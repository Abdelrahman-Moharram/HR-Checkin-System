import math
import pandas as pd
from io import BytesIO
from django.http import HttpResponse

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


def export_as_excel(data, file_name, excluded_cols=[]):
    df = pd.DataFrame(data)
    
    if excluded_cols:
        df = df.drop(excluded_cols, axis=1)


    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
    
    return response

