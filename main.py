import json
from random import randint
from marker import make_map, process_info_for_marker

from optimization_routes import call_sync_api, proccess_json_for_gcloud


# start request dummy info


def get_dummy_deliveries_info(q_deliveries, delivery_block):
    if q_deliveries > 40 or q_deliveries < 1:
        raise Exception('"q_deliveries" max value is 40 and min value is 1"')
    blocks_special_hours = [
        [8, 9, 10, 11],
        [10, 11, 12, 13, 14, 15],
        [16, 17, 18, 19],
    ]

    coordinates = json.loads(
        open("./json/enviaflores_production_direcciones.json").read()
    )

    deliveries = []

    for i in range(q_deliveries):

        location_y = float(coordinates[i].get("gm_lattitude"))
        location_x = float(coordinates[i].get("gm_longitude"))
        # order_id = str(randint(90000, 95000))

        obj = {
            "order_id": f"demo-{i}",
            "location_y": location_y,
            "location_x": location_x,
        }
        if i == 2 or i % 3 == 0 or i == 9:
            block_special_hour = blocks_special_hours[delivery_block - 1]
            start_hour = randint(block_special_hour[0], block_special_hour[-1])
            end_hour = start_hour + 1
            obj.update(
                {
                    "special": {
                        "hour": {
                            "start": f"{str(start_hour)}:00:00",
                            "end": f"{str(end_hour)}:00:00",
                        },
                    },
                }
            )
        deliveries.append(obj)
    return deliveries


# end request dummy info


def run():
    deliveries = get_dummy_deliveries_info(40, 1)

    data_for_request = proccess_json_for_gcloud(
        {
            "shipments": deliveries,
            "drivers": 4,
            "cost_per_traveled_hour": 25,
            "auto_limit": True,
            # "limit_per_driver": 10,
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


if __name__ == "__main__":
    run()
