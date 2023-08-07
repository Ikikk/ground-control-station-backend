import dronekit_sitl as sim
from src.domain.constants import vehicles

'''
dronekit_sitl adalah library yang akan kita gunakan untuk melakukan simulasi tanpa memerlukan wahana
di bawah ini sudah kami siapkan dua simulasi (sitl, sitl2)
'''

# home = vehicles.get(id).home_location
# homepoint = f'--home={latitude},{longitude},0,180'
homepoint = "--home=-7.277704,112.797483,0,180"

class VehicleConfig(object):

    sitl                = sim.start_default()
    connection_string   = sitl.connection_string()
    sitl_args = ['-I0', '--model', 'quad', homepoint] #setting koordinat sitl (latitude, longitude)
    sitl.launch(sitl_args, await_ready=True, restart=True)

    sitl2                = sim.start_default()
    connection_string2   = sitl2.connection_string()
    sitl_args2 = ['-I1', '--model', 'quad', homepoint] #setting koordinat sitl (latitude, longitude)
    sitl2.launch(sitl_args2, await_ready=True, restart=True)
