from dronekit import connect, VehicleMode

# Connect to the Vehicle.
vehicle = connect('COM5', wait_ready=True, baud=57600)

# Get some vehicle attributes (state)
print (" GPS: %s", vehicle.gps_0 )   # settable

# Close vehicle object before exiting script
vehicle.close()

# Shut down simulator
print("Completed")