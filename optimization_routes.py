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


def convert_date(time_zone, date, hour):
    return f"{date}T{hour}-{time_zones[time_zone]}"


def proccess_json_for_gcloud(data: dict, time_zone: str = "General"):

    if not data.get("shipments"):
        raise Exception('"shipments" key is required')

    if not isinstance(data.get("shipments"), list):
        raise Exception('"shipments" must be a list array')

    date = data.get("delivery_date")
    if not date:
        raise Exception('"delivery_date->" key is requried')
    shipments = []
    for shipment in data.get("shipments"):

        delivery = {"label": "", "arrival_location": "", "time_windows": ""}
        label = shipment.get("id")
        if not label:
            raise Exception('"shipments[]->order id" key is required')
        delivery.update({"label": str(label)})
        longitude = shipment.get("longitude")
        if not longitude:
            raise Exception('"shipments[]->longitude" key is required')
        latitude = shipment.get("latitude")
        if not latitude:
            raise Exception('"shipments[]->latitude" key is required')

        delivery.update(
            {
                "arrival_location": {
                    "latitude": latitude,
                    "longitude": longitude,
                }
            }
        )
        schedule = shipment.get("schedule")
        start_delivery_hour = data.get("start_delivery_hour")
        end_delivery_hour = data.get("end_delivery_hour")

        if schedule:

            start_hour = schedule.get("start")
            end_hour = schedule.get("end")
            if not start_hour:
                raise Exception('"shipments[]->schedule->start" key is requried')
            if not end_hour:
                raise Exception('"shipments[]->schedule->end" key is requried')

            start_hour = convert_date(time_zone, date, start_hour)
            end_hour = convert_date(time_zone, date, end_hour)
        elif start_delivery_hour and end_delivery_hour:

            start_hour = convert_date(time_zone, date, start_delivery_hour)
            end_hour = convert_date(time_zone, date, end_delivery_hour)

        else:
            raise Exception(
                'Either "start&&end_delivery_hour" or "shipments[]->schedule" keys are required'
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
            "end_time_windows": [
                {"end_time": convert_date(time_zone, date, end_delivery_hour)}
            ],
            "start_location": {},
            "cost_per_traveled_hour": 0,
        }

        depot_longitude = data.get("depot_longitude")
        depot_latitude = data.get("depot_latitude")

        if not depot_longitude:
            raise Exception('"depot_longitude" key is required')
        if not depot_latitude:
            raise Exception('"depot_latitude" key is required')

        vehicle.update(
            {
                "start_location": {
                    "latitude": depot_latitude,
                    "longitude": depot_longitude,
                },
                "end_location": {
                    "latitude": depot_latitude,
                    "longitude": depot_longitude,
                },
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
            "global_start_time": f"{date}T08:00:00-{time_zones[time_zone]}",
            "global_end_time": f"{date}T20:00:00-{time_zones[time_zone]}",
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
