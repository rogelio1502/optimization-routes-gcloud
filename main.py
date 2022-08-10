import json
from random import randint

from optimization_routes import call_sync_api, proccess_json_for_gcloud


deliveries = []
for i in range(100):

    location_y = float(f"25.{str(randint(70, 99))}")
    location_x = float(f"-100.{str(randint(305, 350))}")
    order_id = str(randint(90000, 95000))

    obj = {
        "order_id": f"demo-{i}",
        "location_y": location_y,
        "location_x": location_x,
    }
    if i == 2 or i % 3 == 0 or i == 9:
        obj.update(
            {
                "special": {
                    "hour": {"start": "10:00:00", "end": "11:00:00"},
                },
            }
        )
    deliveries.append(obj)

data_for_request = proccess_json_for_gcloud(
    {
        "shipments": deliveries,
        "drivers": 25,
        "cost_per_traveled_hour": 0,
        # "auto_limit": True,
        "limit_per_driver": 10,
        "block": 1,
        "depot_location_y": 25.665667776013077,
        "depot_location_x": -100.45060983468106,
    }
)

str_json_response = call_sync_api(json.dumps(data_for_request))

# da = dict(json.loads(str_json_response))
# routes = da.get("routes")
from datetime import datetime, timedelta

utc_start_time = "2022-08-09T15:56:20Z"
utc_start_time_datetime = datetime.strptime(utc_start_time, "%Y-%m-%dT%H:%M:%SZ")
no_utc_start_time_datetime = utc_start_time_datetime - timedelta(hours=5)
print(no_utc_start_time_datetime)
