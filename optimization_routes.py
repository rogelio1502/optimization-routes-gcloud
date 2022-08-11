from datetime import datetime
from re import I
import pytz
from google.cloud import optimization_v1
from google.protobuf.json_format import MessageToJson

project_id = "ef-ecommerce"
time_zones = {
    "General": "05:00",
    "BajaSur": "06:00",
    "BajaNorte": "07:00",
}
blocks = [
    ["08:00:00", "13:00:00"],
    ["10:00:00", "16:00:00"],
    ["13:00:00", "20:00:00"],
]


def convert_date(time_zone, hour):
    return f"{datetime.now(tz=pytz.timezone(f'Mexico/{time_zone}')).strftime('%Y-%m-%d')}T{hour}-{time_zones[time_zone]}"


def proccess_json_for_gcloud(data: dict, time_zone: str = "General"):

    if not data.get("shipments"):
        raise Exception('"shipments" key is required')

    if not isinstance(data.get("shipments"), list):
        raise Exception('"shipments" must be a list array')
    shipments = []
    for shipment in data.get("shipments"):

        delivery = {"label": "", "arrival_location": "", "time_windows": ""}
        label = shipment.get("order_id")
        if not label:
            raise Exception('"shipments[]->order id" key is required')
        delivery.update({"label": label})
        location_x = shipment.get("location_x")
        if not location_x:
            raise Exception('"shipments[]->location_x" key is required')
        location_y = shipment.get("location_y")
        if not location_y:
            raise Exception('"shipments[]->location_y" key is required')

        delivery.update(
            {
                "arrival_location": {
                    "latitude": location_y,
                    "longitude": location_x,
                }
            }
        )
        special_hour = shipment.get("special")
        block = data.get("block")

        if special_hour:

            hour = special_hour.get("hour")
            if not hour:
                raise Exception('"shipments[]->special_hour->hour" key is requried')
            start_hour = hour.get("start")
            end_hour = hour.get("end")
            if not start_hour:
                raise Exception(
                    '"shipments[]->special_hour->hour->start" key is requried'
                )
            if not end_hour:
                raise Exception(
                    '"shipments[]->special_hour->hour->end" key is requried'
                )

            start_hour = convert_date(time_zone, start_hour)
            end_hour = convert_date(time_zone, end_hour)
        elif block:
            try:
                hours = blocks[block - 1]
            except IndexError as e:
                raise Exception('"Block->value" does not exist')
            else:
                start_hour = convert_date(time_zone, hours[0])
                end_hour = convert_date(time_zone, hours[1])

        else:
            raise Exception(
                'Either "block" or "shipments[]->special_hour" keys are required'
            )

        delivery.update(
            {"time_windows": [{"start_time": start_hour, "end_time": end_hour}]}
        )

        shipments.append(
            {
                "deliveries": [delivery],
                "loadDemands": {"weight": {"amount": "1"}},
            }
        )

    vehicles = []
    drivers = data.get("drivers")

    auto_limit = data.get("auto_limit")
    limit_per_driver = data.get("limit_per_driver")

    if auto_limit:

        _limit = len(shipments) / drivers
        limit = int(_limit + len(shipments) % drivers)
    elif limit_per_driver:

        limit = limit_per_driver
    else:
        raise Exception('"limit_per_driver" or "auto_limit" keys are required')

    for driver in range(drivers):
        vehicle = {
            "end_time_windows": [{"end_time": convert_date(time_zone, hours[1])}],
            "start_location": {},
            "cost_per_traveled_hour": 0,
        }

        depot_location_x = data.get("depot_location_x")
        depot_location_y = data.get("depot_location_y")

        if not depot_location_x:
            raise Exception('"depot_location_x" key is required')
        if not depot_location_y:
            raise Exception('"depot_location_y" key is required')

        vehicle.update(
            {
                "start_location": {
                    "latitude": depot_location_y,
                    "longitude": depot_location_x,
                }
            }
        )

        cost_per_traveled_hour = data.get("cost_per_traveled_hour")

        if cost_per_traveled_hour:
            vehicle.update(
                {
                    "cost_per_traveled_hour": int(cost_per_traveled_hour)
                    if cost_per_traveled_hour
                    else 0
                }
            )

        vehicle.update(
            {
                "loadLimits": {"weight": {"maxLoad": limit}},
            }
        )

        vehicles.append(vehicle)

    finished_json = {
        "model": {
            "global_start_time": f"{datetime.now().strftime('%Y-%m-%d')}T08:00:00-{time_zones[time_zone]}",
            "global_end_time": f"{datetime.now().strftime('%Y-%m-%d')}T20:00:00-{time_zones[time_zone]}",
            "shipments": shipments,
            "vehicles": vehicles,
        }
    }

    return finished_json


def call_sync_api(json_deliveries: dict) -> None:
    """Call the sync api for fleet routing."""

    fleet_routing_client = optimization_v1.FleetRoutingClient()

    fleet_routing_request = optimization_v1.OptimizeToursRequest.from_json(
        json_deliveries
    )
    fleet_routing_request.parent = f"projects/{project_id}"

    fleet_routing_response = fleet_routing_client.optimize_tours(
        fleet_routing_request, timeout=100
    )

    json_obj = MessageToJson(fleet_routing_response._pb)

    with open("./json/routes.json", "w") as convert_file:
        convert_file.write(json_obj)

    return json_obj
