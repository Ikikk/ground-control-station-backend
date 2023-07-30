'''
berikut ini merupakan global variabel
'''
vehicles = {} # list vehicles

vehicle_dataList = [] # each item = (id:{key, vehicleColor, address, baudrate, isConnected, home, missionList})
waypoint_list = [] # each item = (id:{lon,lat})
homepoint_list = [] # each item = (id:{lon,lat})
mission_list = [] # each item = (id:{value})
mssionlist = [] # untuk command string
mission_all = []
sequenced_mission = []
listeners_location = []

SEQ_MISSION_RUNNING = False
START_MISSION_TIME = ""