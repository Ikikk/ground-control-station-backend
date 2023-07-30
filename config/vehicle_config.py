import dronekit_sitl as sim

'''
dronekit_sitl adalah library yang akan kita gunakan untuk melakukan simulasi tanpa memerlukan wahana
di bawah ini sudah kami siapkan dua simulasi (sitl, sitl2)
'''

class VehicleConfig(object):

    sitl                = sim.start_default()
    connection_string   = sitl.connection_string()
    sitl_args = ['-I0', '--model', 'quad', '--home=-8.5400335,115.4919740,0,180'] #setting koordinat sitl (latitude, longitude)
    sitl.launch(sitl_args, await_ready=True, restart=True)

    sitl2                = sim.start_default()
    connection_string2   = sitl2.connection_string()
    sitl_args2 = ['-I1', '--model', 'quad', '--home=-8.5400394,115.4919995,0,180'] #setting koordinat sitl (latitude, longitude)
    sitl2.launch(sitl_args2, await_ready=True, restart=True)