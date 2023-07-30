from flask import request, jsonify
import datetime
from src.create_app import create_app
from config.vehicle_config import VehicleConfig

app = create_app(VehicleConfig)
# Never cache
@app.after_request
def never_cache(response):
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.before_request
def check_for_maintenance():
    service_context_service = app.container.service_context_service()
    status = service_context_service.get_service_context()

    if not ("maintenance" in request.path or "status" in request.path):
        if status.maintenance:
            return jsonify(
                {"message": "Service is currently enduring maintenance"}
            ), 503

# def main():
#     app.run(threaded=True, host='127.0.0.1', port=5000)

if __name__ == "__main__":
    # main()
    app.run(host='127.0.0.1', port=5000, threaded=True)