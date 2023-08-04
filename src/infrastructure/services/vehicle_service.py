# src/infrastructure/services/vehicle_service.py

from datetime import datetime
import json
from queue import Queue
from flask import request
import time
import mpu
from src.domain.constants import vehicles, listeners_location, SEQ_MISSION_RUNNING, START_MISSION_TIME
from src.domain.exceptions import sse_encode, state_msg
from dronekit import VehicleMode, LocationGlobalRelative, Command

SEQ_MISSION_RUNNING = True
global mission_num

'''
Melakukan threading untuk men-generate informasi terbarukan vehicle
'''
from threading import Thread
import time
def tcount():
    while True:
        time.sleep(0.25)
        try:
            for id in vehicles:
                msg = state_msg(id)
                for x in listeners_location:
                    x.put(msg)
        except Exception as e:
            pass
t = Thread(target=tcount)
t.daemon = True
t.start()

def get_lat():
    lat = None
    if request.method == 'POST' or request.method == 'PUT':
        try:
            lat = request.json['lat']
        except Exception as e:
            print("[Controller] Line 43: exception in get_lat_lon ", e)
    return lat

def get_lon():
    lon = None
    if request.method == 'POST' or request.method == 'PUT':
        try:
            lon = request.json['lon']
        except Exception as e:
            print("[Controller] Line 43: exception in get_lat_lon ", e)
    return lon

def arm_and_takeoff(id, aTargetAltitude, mission_num):
    # Your code here to get the drone state based on the given ID
        
    print("[Service] Line 37 : V ", id, " :: Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicles.get(id).is_armable:
        print("[Service] Line 40 : V ", id, " :: Waiting for vehicle to initialise...")
        time.sleep(1)
        
    print("[Service] Line 43 : V ", id, " :: Arming motors")
    # Copter should arm in GUIDED mode
    print("\n[Service] Line 45 : Set Vehicle.mode = GUIDED (currently: %s)" % vehicles.get(id).mode.name) 
    vehicles.get(id).mode = VehicleMode("GUIDED")
    
    while not vehicles.get(id).mode.name =='GUIDED':  #Wait until mode has changed
        print(" [Service] Line 49 : Waiting for mode change ...")
        time.sleep(1)
        
    vehicles.get(id).armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicles.get(id).armed:
        print("[Service] Line 56 : V ", id, " :: Waiting for arming...")
        time.sleep(1)

    print("[Service] Line 59 : V ", id, " :: Taking off!")
    vehicles.get(id).simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        # LOG
        now = datetime.now()
        CURRENT_TIME = now.strftime("%d-%m-%Y %H:%M:%S")

        f = open("{TIME}.tsv".format(TIME=START_MISSION_TIME), "a")
        f.write("{CURRENT_TIME}\t{RUNNING_MISSION}\t{VEHICLE}\t{ARMED}\t{MODE}\t{HEADING}\t{VSPEED}\t{GSPEED}\t{LON}\t{LAT}\t{ALT}\r\n".format(
            CURRENT_TIME=CURRENT_TIME,
            RUNNING_MISSION=mission_num,
            VEHICLE=id,
            ARMED= "YES" if vehicles.get(id).armed == True else "NO",
            MODE=vehicles.get(id).mode.name,
            VSPEED=vehicles.get(id).airspeed,
            GSPEED=vehicles.get(id).groundspeed,
            HEADING=vehicles.get(id).heading or 0,
            LON=vehicles.get(id).location.global_relative_frame.lon,
            LAT=vehicles.get(id).location.global_relative_frame.lat,
            ALT=vehicles.get(id).location.global_relative_frame.alt
        ))

        f.close()
        
        print("[Service] Line 87 : V ", id, " :: Altitude: ", vehicles.get(id).location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicles.get(id).location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("[Service] Line 90 : V ", id, " :: Reached target altitude")
            break

        # FAILSAFE JIKA BARONYA TIBA2 minus lebih dari 4
        if vehicles.get(id).location.global_relative_frame.alt <= -4:
            SEQ_MISSION_RUNNING == False
            vehicles.get(id).mode = VehicleMode("LAND")
            print("[Service] Line 97 : ::: ABORTED :::")
            print("[Service] Line 98 : Vehicle Mode ", vehicles.get(id).mode)
            return "ABORT SUCCESS"
            
        time.sleep(0.5)

def distance_to_destination(id, coord2):
    lon = vehicles.get(id).location.global_relative_frame.lon
    lat = vehicles.get(id).location.global_relative_frame.lat
    coord1 = (lat, lon)
    dist = mpu.haversine_distance(coord1, coord2)
    print("[Service] Line 108 : haversine_distance for nextion ", dist)
    return dist

def goto(miss, mission_num):
    global SEQ_MISSION_RUNNING
    global vehicles

    vehicle_id = int(miss.get('id'))
    dest_lat = miss.get('lat')
    dest_lon = miss.get('lon')
    command = miss.get('cmd')
    alt = float(miss.get('alt'))

    vehicles.get(vehicle_id).airspeed = 1
    vehicles.get(vehicle_id).groundspeed = 1
    point = LocationGlobalRelative(dest_lat, dest_lon, alt)
    vehicles.get(vehicle_id).simple_goto(point)

    while distance_to_destination(vehicle_id, (dest_lat, dest_lon)) > 0.001:
        # LOG
        now = datetime.now()
        CURRENT_TIME = now.strftime("%d-%m-%Y %H:%M:%S")

        f = open("{TIME}.tsv".format(TIME=START_MISSION_TIME), "a")
        f.write("{CURRENT_TIME}\t{RUNNING_MISSION}\t{VEHICLE}\t{ARMED}\t{MODE}\t{HEADING}\t{VSPEED}\t{GSPEED}\t{LON}\t{LAT}\t{ALT}\r\n".format(
            CURRENT_TIME=CURRENT_TIME,
            RUNNING_MISSION=mission_num,
            VEHICLE=vehicle_id,
            ARMED= "YES" if vehicles.get(vehicle_id).armed == True else "NO",
            MODE=vehicles.get(vehicle_id).mode.name,
            VSPEED=vehicles.get(vehicle_id).airspeed,
            GSPEED=vehicles.get(vehicle_id).groundspeed,
            HEADING=vehicles.get(vehicle_id).heading or 0,
            LON=vehicles.get(vehicle_id).location.global_relative_frame.lon,
            LAT=vehicles.get(vehicle_id).location.global_relative_frame.lat,
            ALT=vehicles.get(vehicle_id).location.global_relative_frame.alt
        ))
        
        f.close()

        if SEQ_MISSION_RUNNING == False:
            vehicles.get(vehicle_id).mode = VehicleMode("LAND")
            print("[Service] Line 150 : ::: ABORTED :::")
            print("[Service] Line 151 : Vehicle Mode ", vehicles.get(vehicle_id).mode)
            return "ABORT SUCCESS"

        print(" [Service] Line 154 : Waiting vehicle ", vehicle_id, "to waypoint", mission_num-1)
        print("[Service] Line 155 : Vehicle Mode ", vehicles.get(vehicle_id).mode)
        time.sleep(0.5)

def land(vehicle_id, mission_num):
    global SEQ_MISSION_RUNNING
    global vehicles
    vehicles.get(vehicle_id).mode = VehicleMode("LAND")

    # WAIT UNTIL VEHILCE IS NOT ARMED
    while True:
        print(" [Service] Line 165 : Waiting vehicle ", vehicle_id, "landed")
        # LOG
        now = datetime.now()
        CURRENT_TIME = now.strftime("%d-%m-%Y %H:%M:%S")

        f = open("{TIME}.tsv".format(TIME=START_MISSION_TIME), "a")
        f.write("{CURRENT_TIME}\t{RUNNING_MISSION}\t{VEHICLE}\t{ARMED}\t{MODE}\t{HEADING}\t{VSPEED}\t{GSPEED}\t{LON}\t{LAT}\t{ALT}\r\n".format(
            CURRENT_TIME=CURRENT_TIME,
            RUNNING_MISSION=mission_num,
            VEHICLE=vehicle_id,
            ARMED= "YES" if vehicles.get(vehicle_id).armed == True else "NO",
            MODE=vehicles.get(vehicle_id).mode.name,
            VSPEED=vehicles.get(vehicle_id).airspeed,
            GSPEED=vehicles.get(vehicle_id).groundspeed,
            HEADING=vehicles.get(vehicle_id).heading or 0,
            LON=vehicles.get(vehicle_id).location.global_relative_frame.lon,
            LAT=vehicles.get(vehicle_id).location.global_relative_frame.lat,
            ALT=vehicles.get(vehicle_id).location.global_relative_frame.alt
        ))
        
        f.close()

        if vehicles.get(vehicle_id).armed == False:
            return "DONE"
        
        time.sleep(1)
        
def do_mission(missions):
    global SEQ_MISSION_RUNNING
    SEQ_MISSION_RUNNING = True
    global vehicles
    global START_MISSION_TIME

    # LOG ALL MISSION
    now = datetime.now()
    counter = 0
    START_MISSION_TIME = now.strftime("%d-%m-%Y %H-%M-%S")
    f = open("{TIME}.tsv".format(TIME=START_MISSION_TIME), "a")
    f.write("MISSION LIST\r\n")
    f.write("NUM\tCOMMAND\tVEHICLE\tLON\tLAT\tALT\tWAIT NEXT\r\n")

    for mission in missions:
        for miss in mission:
            counter = counter+1
            vehicle_id = int(miss.get('id'))
            dest_lat = miss.get('lat')
            dest_lon = miss.get('lon')
            command = miss.get('cmd')
            alt = float(miss.get('alt'))
            wait_next = "Yes" if miss.get('wait_next') == True else "No"
            f.write("{NUM}\t{COMMAND}\t{VEHICLE}\t{LON}\t{LAT}\t{ALT}\t{WAIT_NEXT}\r\n".format(
                NUM=counter,
                COMMAND=command,
                VEHICLE=counter,
                LON=dest_lon,
                LAT=dest_lat,
                ALT=alt,
                WAIT_NEXT=wait_next
            ))
    
    f.write("\r\nLOGS\r\n")
    f.write("TIME\tRUNNING MISSION\tVEHICLE\tARMED\tMODE\tHEADING\tVSPEED\tGSPEED\tLON\tLAT\tALT\r\n")
    f.close()

    counter = 0
    for mission in missions:
        func_in_thread = []
        for miss in mission:
            print(miss)
            counter = counter+1
            vehicle_id = int(miss.get('id'))
            dest_lat = miss.get('lat')
            dest_lon = miss.get('lon')
            command = miss.get('cmd')
            alt = float(miss.get('alt'))

            # ABORT MISSION TRIGERRED
            if SEQ_MISSION_RUNNING == False:
                vehicles.get(vehicle_id).mode = VehicleMode("LAND")
                print("[Service] Line 244 : ::: ABORTED :::")
                print("[Service] Line 245 : Vehicle Mode ", vehicles.get(vehicle_id).mode)
                return "ABORT SUCCESS"

            print(" [Service] Line 248 : Mission ", counter ,"Runned by Vehicle ::", vehicle_id)
            if command == 'TAKEOFF':
                print(" [Service] Line 250 : TAKE OFF ")
                func_in_thread.append(Thread( target=arm_and_takeoff, args=(vehicle_id, alt, counter)))

            elif command == 'WAYPOINT':
                print(" [Service] Line 254 : Going to : ", mission)
                func_in_thread.append(Thread( target=goto, args=(miss, counter)))
            elif command == 'DELAY':
                print(" [Service] Line 257 : SLEEP 5 Seconds ")
                time.sleep(5)
            elif command == 'LAND':
                print(" [Service] Line 260 : LANDING ")
                func_in_thread.append(Thread( target=land, args=(vehicle_id, counter)))

        # Start T1hread
        for thrd in func_in_thread:
            thrd.start()

        # Wait for Thread Stopped
        for thrd in func_in_thread:
            thrd.join()

def readmission_file(aFileName, id):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % aFileName)
    global vehicles
    cmds = vehicles.get(id).commands
    missionlist=[]
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])
                ln_autocontinue=int(linearray[11].strip())
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist
    
def readmission_text(mission_text, id):
    global vehicles
    cmds = vehicles.get(id).commands
    missionlist=[]
    data = mission_text.split("\n")
    i=0
    for line in data:
        print("[Service] Line 311 : line :")
        print("[Service] Line 312 : line ", line)
        if i!=0 and len(line)>0:
            linearray=line.split('\t')
            ln_index=int(linearray[0])
            ln_currentwp=int(linearray[1])
            ln_frame=int(linearray[2])
            ln_command=int(linearray[3])
            ln_param1=float(linearray[4])
            ln_param2=float(linearray[5])
            ln_param3=float(linearray[6])
            ln_param4=float(linearray[7])
            ln_param5=float(linearray[8])
            ln_param6=float(linearray[9])
            ln_param7=float(linearray[10])
            ln_autocontinue=int(linearray[11].strip())
            cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
            missionlist.append(cmd)       
        i+=1         
    return missionlist
    
def upload_mission_file(aFileName, id):
    """
    Upload a mission from a file. 
    """
    global vehicles
    #Read mission from file
    missionlist = readmission_file(aFileName, id)
    
    print("\n[Service] Line 340 : Upload mission from a file: %s" % aFileName)
    #Clear existing mission from vehicle
    print(' [Service] Line 342 : Clear mission')
    cmds = vehicles.get(id).commands
    cmds.clear()
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' [Service] Line 348 : Upload mission')
    vehicles.get(id).commands.upload()

def upload_mission_text(mission_text, id):
    """
    Upload a mission from a text mission. 
    """
    global vehicles
    #Read mission from file
    missionlist = []
    readmission_text(mission_text, id)
    
    print("\n[Service] Line 360 : Upload mission from a text:\n%s" % mission_text)
    #Clear existing mission from vehicle
    print(' [Service] Line 362 : Clear mission')
    cmds = vehicles.get(id).commands
    cmds.clear()
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' [Service] Line 368 : Upload mission')
    vehicles.get(id).commands.upload()


def gen():
    q = Queue()
    listeners_location.append(q)
    try:
        while True:
            result = q.get()
            ev = sse_encode(result)
            yield ev.encode()
    except GeneratorExit: # Or maybe use flask signals
        listeners_location.remove(q)
        