import json
from marker import make_map, process_info_for_marker
from optimization_routes import call_sync_api, proccess_json_for_gcloud


def run():

    json_payload = json.loads(open("./json/orders.json").read())

    # get info from payload
    deliveries = json_payload.get("orders")
    drivers = json_payload.get("drivers")
    cost_per_traveled_hour = json_payload.get("cost_per_traveled_hour")
    limit_per_driver = json_payload.get("limit_per_driver")
    start_delivery_hour = json_payload.get("start_delivery_hour")
    end_delivery_hour = json_payload.get("end_delivery_hour")
    depot_latitude = json_payload.get("depot_latitude")
    depot_longitude = json_payload.get("depot_longitude")
    time_zone = json_payload.get("time_zone")
    date = json_payload.get("date")

    # format json for gcloud
    data_for_request = proccess_json_for_gcloud(
        {
            "shipments": deliveries,
            "drivers": drivers,
            "cost_per_traveled_hour": cost_per_traveled_hour,
            "limit_per_driver": limit_per_driver,
            "start_delivery_hour": start_delivery_hour,
            "end_delivery_hour": end_delivery_hour,
            "depot_latitude": depot_latitude,
            "depot_longitude": depot_longitude,
            "delivery_date": date,
        },
        time_zone=time_zone,
    )

    # call optimization api
    str_json_response = call_sync_api(json.dumps(data_for_request))

    # process info for maker
    info_for_marker = process_info_for_marker(json.loads(str_json_response), deliveries)

    # make map
    make_map(info_for_marker)


if __name__ == "__main__":
    run()
