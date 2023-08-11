import json
from src.domain.constants import vehicles
import numpy as np
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
    
    pitch = vehicles.get(id).attitude.pitch
    yaw = vehicles.get(id).attitude.yaw
    roll = vehicles.get(id).attitude.roll

    return {
        "id": vehicles.get(id).id, #return id vehicle
        "armable": vehicles.get(id).is_armable, #return boolean
        "armed": vehicles.get(id).armed, #return boolean
        "alt": vehicles.get(id).location.global_relative_frame.alt, #return 
        "mode": vehicles.get(id).mode.name,
        "heading": vehicles.get(id).heading or 0,
        "vspeed":vehicles.get(id).airspeed,
        "gspeed":vehicles.get(id).groundspeed,
        "lat": vehicles.get(id).location.global_relative_frame.lat,
        "lon": vehicles.get(id).location.global_relative_frame.lon, 
        "vel": vehicles.get(id).velocity,
        "pitch": np.rad2deg(pitch),
        "roll": np.rad2deg(roll),
        "yaw": np.rad2deg(yaw),
        "ekf": vehicles.get(id).ekf_ok,
        "lasthb": vehicles.get(id).last_heartbeat,
        "systat": vehicles.get(id).system_status.state,
        "home_dist": vehicles.get(id).location.local_frame.distance_home(), #meters
        "hdop": vehicles.get(id).gps_0.eph, #horizontal dilution of position-hdop (int)
        "vdop": vehicles.get(id).gps_0.epv, #vertical dilution of position-vdop (int)
        "fix_type": vehicles.get(id).gps_0.fix_type, #0-1:no fix, 2: 2D fix, 3: 3D fix (int)
        "sats": vehicles.get(id).gps_0.satellites_visible, #number of satellites visible (int)
    }
