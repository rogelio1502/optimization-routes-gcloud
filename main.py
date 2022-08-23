import json
from marker import make_map, process_info_for_marker
from optimization_routes import call_sync_api, proccess_json_for_gcloud


def run():

    start_hour = "8"
    end_hour = "12"
    deliveries = json.loads(open("./json/orders.json").read())

    data_for_request = proccess_json_for_gcloud(
        {
            "shipments": deliveries,
            "drivers": 20,
            "cost_per_traveled_hour": 30,
            "limit_per_driver": 20,
            "start_delivery_hour": f"{str(start_hour)}:00:00",
            "end_delivery_hour": f"{str(end_hour)}:00:00",
            "depot_latitude": 25.665667776013077,
            "depot_longitude": -100.45060983468106,
        },
        time_zone="General",
    )

    str_json_response = call_sync_api(json.dumps(data_for_request))
    info_for_marker = process_info_for_marker(json.loads(str_json_response), deliveries)
    make_map(info_for_marker)


if __name__ == "__main__":
    run()
