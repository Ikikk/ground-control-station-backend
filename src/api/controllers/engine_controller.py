# src/api/controllers/engine_controller.py
import time
from flask import Blueprint, jsonify, Response, request
from src.infrastructure.services import arm_and_takeoff, do_mission, upload_mission_text, gen, str2bool
from src.domain.constants import vehicles, vehicle_dataList, homepoint_list, waypoint_list, mission_all, mission_list
from src.domain.exceptions import sse_encode, state_msg
# from config.vehicle_config import VehicleConfig
from dronekit import VehicleMode, LocationGlobalRelative, connect

global latitude
global longitude

drone_api = Blueprint('engine_controller', __name__)

'''
API dalam melakukan koneksi ke vehicle
'''
@drone_api.route("/connect", methods=['POST',  'PUT'])
def api_connect():
    if request.method =='POST' or request.method == 'PUT':
        try:
            addr = request.json['addr']
            baudrate = request.json['baudrate']
            id = int(request.json['id'])
            # latitude = request.json['lat']
            # longitude = request.json['lon']

            # home = f'--home={latitude},{longitude},0,180'

            # VehicleConfig.sitl_args = ['-I0', '--model', 'quad', home]
            # VehicleConfig.sitl_args2 = ['-I1', '--model', 'quad', home]

            print('[Controller] Line 22 : connecting to drone...')
            nvehicle = None
            try:
                '''
                timeout = lama waktu menunggu vehicle terkoneksi
                heartbeat_timeout = waktu yang dibutuhkan untuk terkoneksi kembali jika lost connection
                '''
                nvehicle = connect(str(addr), wait_ready=True, timeout=120, heartbeat_timeout=90, baud=int(baudrate))
                nvehicle.id = id
                vehicles[id] = nvehicle
                # vehicles.append(nvehicle)
                print("[Controller] Line 34 : airspeed ", vehicles.get(id).airspeed)
                vehicles.get(id).parameters['ARMING_CHECK'] = 0
                vehicles.get(id).flush()
                print("[Controller] Line 37 :Vehicle Connected")
            except Exception as e:
                nvehicle.close()
                print('[Controller] Line 40 :waiting for connection... (%s)' % str(e))
                return jsonify(error=1, msg="Failed to Connect to Vehicle")

            if not nvehicle:
                return jsonify(error=1,msg="Failed to Connect to Vehicle")
            else:
                nlon = vehicles.get(id).location.global_relative_frame.lon
                nlat = vehicles.get(id).location.global_relative_frame.lat
                return jsonify(error=0, msg="Connection success", lon=nlon, lat=nlat)
        except Exception as e:
            print("[Controller] Line 48 : Exception in api_connect ", e)
            return jsonify(error=1, msg="Failed to Connect to Vehicle")

    # Handle invalid request method
    return jsonify(error=1, msg="Invalid request method")

'''
API dalam memutuskan koneksi vehicle
'''
@drone_api.route("/disconnect", methods=['POST','PUT'])
def api_disconnect():
    if request.method =='POST' or request.method == 'PUT':
        try:
            id = int(request.json['id'])
            print("[Controller] Line 62 : vehicles ", vehicles)
            print("[Controller] Line 63 : id ", id)
            if id in vehicles:
                vehicles.get(id).close()
                vehicles.pop(id)
                print("[Controller] Line 67 : Vehicle Disconnected")
            else : print("[Controller] Line 68 : No vehicle with id %d" % id)
            return jsonify(error=0, msg="Disconnect success")
        except Exception as e:
            print("[Controller] Line 71 : exception in api_disconnect ", e)
            return jsonify(error=1, msg="Failed to Disconnect")

'''
API dalam melakukan update informasi terbarukan vehicle
'''
@drone_api.route("/sse/state")
def api_sse_location():
    gens = gen()
    return Response(gens, mimetype="text/event-stream")

'''
API untuk melakukan transfer data dari front-end ke back-end
'''
@drone_api.route("/update_data", methods=['POST','PUT'])
def update_data():
    global vehicle_dataList
    global homepoint_list
    global waypoint_list
    global mission_list
    global mission_all
    if request.method =='POST' or request.method == 'PUT':
        try:
            data_type = request.json['type']

            data = request.json['data']
            if data_type == "vehicle_dataList":
                vehicle_dataList = []
                for value in data:
                    vehicle_dataList.append(value)
                print("[Controller] Line 100 : vehicle_datalist ", vehicle_dataList)
            elif data_type == "homepoint_list":
                homepoint_list = []
                for value in data:
                    homepoint_list.append(value)
                print("[Controller] Line 105 : homepoint_list ", homepoint_list)
            elif data_type == "waypoint_list":
                waypoint_list = []
                for value in data:
                    waypoint_list.append(value)
                print("[Controller] Line 110 : waypoint_list ", waypoint_list)
            elif data_type == "mission_list":
                mission_list = []
                for value in data:
                    mission_list.append(value)
                print("[Controller] Line 115 : mission_list ", mission_list)
            elif data_type == "mission_all":
                mission_all = []
                for value in data:
                    mission_all.append(value)
                print("[Controller] Line 120 : mission_all ", mission_all)
            return "success"
        except Exception as e:
            print("[Controller] Line 123 : Exception in update_data ", e)
            return "failed"

'''
API untuk melakukan transfer data dari back-end ke front-end
'''
@drone_api.route("/get_data", methods=['POST','PUT'])
def get_data():
    global vehicle_dataList
    global homepoint_list
    global waypoint_list
    global mission_list
    global mission_all
    if request.method =='POST' or request.method == 'PUT':
        try:
            data_request = request.json['request']
            if data_request == "vehicle_dataList":
                print("[Controller] Line 140 : vehicle_dataList:")
                print("[Controller] Line 141: vehicle_datalist ", vehicle_dataList)
                return jsonify(error=0, data=vehicle_dataList)
            elif data_request == "homepoint_list":
                print("[Controller] Line 144 : homepoint_list:")
                print("[Controller] Line 145 : homepoint_list ", homepoint_list)
                return jsonify(error=0, data=homepoint_list)
            elif data_request == "waypoint_list":
                print("[Controller] Line 148 : waypoint_list:")
                print("[Controller] Line 149 : waypoint_list ", waypoint_list)
                return jsonify(error=0, data=waypoint_list)
            elif data_request == "mission_list":
                print("[Controller] Line 152 : mission_list:")
                print("[Controller] Line 153 : mission_list ", mission_list)
                return jsonify(error=0, data=mission_list)
            elif data_request == "mission_all":
                print("[Controller] Line 156 : mission_all:")
                print("[Controller] Line 157 : mission_all ", mission_all)
                return jsonify(error=0, data=mission_all)
        except Exception as e:
            print("[Controller] Line 160 : exception in get_data ", e)
            return "failed"

'''
API Import mission from given file path
'''

@drone_api.route("/import_mission", methods=['POST','PUT'])
def import_mission():
    if request.method =='POST' or request.method == 'PUT':
        try:
            state_data = request.json['state']
            waypoints = state_data['waypoints']
            wp_list = [[waypoint['lon'], waypoint['lat']] for waypoint in waypoints]

            return jsonify(wp=wp_list)
        except Exception as e:
            print("[Controller] Line 177 : exception in import_mission ", e)
            return "failed"


'''
API Upload mission to vehicle
'''
@drone_api.route("/upload_mission", methods=['POST','PUT'])
def upload_mission():
    global vehicles
    if request.method =='POST' or request.method == 'PUT':
        try:
            vehicle_id = request.json['id']
            mission_text = request.json['mission_text']
            
            print("[Controller] Line 192 : mission_text:")
            print("[Controller] Line 193 : mission_text ", mission_text)
            upload_mission_text(mission_text, vehicle_id)
            return "Upload success"
        except Exception as e:
            print("[Controller] Line 197 : exception in upload_mission ", e)
            return "failed"

'''
API dalam melakukan arming secara otomatis
'''
@drone_api.route("/arm", methods=['POST', 'PUT'])
def api_location():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            id = int(request.json['id'])
            arm_and_takeoff(int(request.json['alt'], id))
            vehicles.get(id).armed = True
            vehicles.get(id).flush()
            return jsonify(ok=True)
        except Exception as e:
            print("[Controller] Line 213 : exception in api_location ", e)
            return jsonify(ok=False)

'''
API untuk terbang secara urut
'''
@drone_api.route("/start_seq_mission", methods=['POST','PUT'])
def start_seq_mission():
    global sequenced_mission
    # global lat
    # global lon
    sequenced_mission = []
    temp_mission = []
    if request.method == 'POST' or request.method == 'PUT':
        try:
            data = request.json['data']
            # lat = request.json['lat']
            # lon = request.json['lon']
            # get_lat()
            # get_lon()
            # get_lon(lon)
            for item in data:
                item_formated = {
                    'id':int(item['vehicle_id']),
                    'cmd':item['mission'],
                    'lat':float(item['lat']),
                    'lon':float(item['lon']),
                    'alt':float(item['alt']),
                    'wait_next':str2bool(item['wait_next']),
                    'complete':False
                }
                temp_mission.append(item_formated)
        except Exception as e:
            print("[Controller] Line 239 : exception in start_mission ", e)
        
        # Then format the mission
        data_append = []
        for miss in temp_mission:
            data_append.append(miss)

            if miss.get('wait_next') == True:
                sequenced_mission.append(data_append)
                data_append = []
        
        if len(data_append) > 0:
            sequenced_mission.append(data_append)
            data_append = []
        
        do_mission(sequenced_mission)
        return "success"

'''
API untuk batalkan terbang secara urut
'''
@drone_api.route("/abort_seq_mission", methods=['POST','PUT'])
def abort_seq_mission():
    global SEQ_MISSION_RUNNING
    SEQ_MISSION_RUNNING = False
    return "success"

'''
API untuk mengubah mode vehicle
'''
@drone_api.route("/mode", methods=['POST', 'PUT'])
def api_mode():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            id = int(request.json['id'])
            vehicles.get(id).mode = VehicleMode(request.json['mode'].upper())
            vehicles.get(id).flush()
            return jsonify(ok=True)
        except Exception as e:
            print("[Controller] Line 278 : exception in api_mode ", e)
            return jsonify(ok=False)

'''
API untuk menggerakan vehicle ke titik yang diinginkan
'''
@drone_api.route("/goto", methods=['POST', 'PUT'])
def api_goto():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            id = int(request.json['id'])
            waypoints=request.json['waypoints']
            print("[Controller] Line 290 : Set default/target airspeed to 3")
            vehicles.get(id).airspeed = 3
            for xy in waypoints:
                print("[Controller] Line 293 : Going to : lat ", xy[1] , " long : " , xy[0])
                waypoint = LocationGlobalRelative(float(xy[1]), float(xy[0]), 20)
                vehicles.get(id).simple_goto(waypoint)
                time.sleep(30)

            vehicles.get(id).mode = VehicleMode(request.json['mode'].upper())
            vehicles.get(id).flush()
            return "ok"
        except Exception as e:
            print("[Controller] Line 302 : exception in api_goto ", e)
            return "failed"

