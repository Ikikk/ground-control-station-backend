# src/api/schemas/drone_schemas.py

# Your code here to define the data schemas for drones
class Droneschemas:
    def __init__(self, id, armed, altitude, mode, heading, vspeed, gspeed, latitude, longitude):
        self.id = id
        self.armed = armed
        self.altitude = altitude
        self.mode = mode
        self.heading = heading
        self.vspeed = vspeed
        self.gspeed = gspeed
        self.latitude = latitude
        self.longitude = longitude