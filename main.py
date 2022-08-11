import json
from random import randint
from marker import make_map, process_info_for_marker

from optimization_routes import call_sync_api, proccess_json_for_gcloud


coordinates = json.loads(open("./json/enviaflores_production_direcciones.json").read())


deliveries = []

for i in range(40):

    location_y = float(coordinates[i].get("gm_lattitude"))
    location_x = float(coordinates[i].get("gm_longitude"))
    order_id = str(randint(90000, 95000))

    obj = {
        "order_id": f"demo-{i}",
        "location_y": location_y,
        "location_x": location_x,
    }

    deliveries.append(obj)


data_for_request = proccess_json_for_gcloud(
    {
        "shipments": deliveries,
        "drivers": 4,
        "cost_per_traveled_hour": 25,
        # "auto_limit": True,
        "limit_per_driver": 10,
        "block": 1,
        "depot_location_y": 25.665667776013077,
        "depot_location_x": -100.45060983468106,
    }
)


str_json_response = call_sync_api(json.dumps(data_for_request))
info_for_marker = process_info_for_marker(json.loads(str_json_response), deliveries)
make_map(info_for_marker)
# da = dict(json.loads(str_json_response))
# routes = da.get("routes")
# from datetime import datetime, timedelta

# utc_start_time = "2022-08-09T15:56:20Z"
# utc_start_time_datetime = datetime.strptime(utc_start_time, "%Y-%m-%dT%H:%M:%SZ")
# no_utc_start_time_datetime = utc_start_time_datetime - timedelta(hours=5)
# print(no_utc_start_time_datetime)
