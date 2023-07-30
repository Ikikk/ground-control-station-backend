import json
from src.domain.constants import vehicles
'''
berikut ini merupakan block code untuk memberikan informasi terbarukan tentang vehicle yang telah terkoneksi
'''
def sse_encode(obj, id=None):
    return "data: %s\n\n" % json.dumps(obj)

def state_msg(id):
    if vehicles.get(id).location.global_relative_frame.lat == None:
        raise Exception('no position info')
    if vehicles.get(id).armed == None:
        raise Exception('no armed info')
    return {
        "id": vehicles.get(id).id,
        "armed": vehicles.get(id).armed,
        "alt": vehicles.get(id).location.global_relative_frame.alt,
        "mode": vehicles.get(id).mode.name,
        "heading": vehicles.get(id).heading or 0,
        "vspeed":vehicles.get(id).airspeed,
        "gspeed":vehicles.get(id).groundspeed,
        "lat": vehicles.get(id).location.global_relative_frame.lat,
        "lon": vehicles.get(id).location.global_relative_frame.lon
    }
