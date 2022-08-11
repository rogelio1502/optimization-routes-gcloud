import json
from turtle import width
import folium

colors = ["blue", "white", "yellow", "orange", "rgb(180, 240, 80)"]


def process_info_for_marker(info: dict, deliveries_locations: list):
    # print(type(info))
    # print(info.get("metrics"))

    info_for_marker = []

    routes = info.get("routes")
    if routes:

        c = 0
        for i in routes:
            c += 1
            obj = {"route": c}
            _visits = []
            visits = i.get("visits")
            for i in visits:
                _visit = {"order_id": i.get("visitLabel")}
                odd = filter(
                    lambda delivery: dict(delivery).get("order_id")
                    == i.get("visitLabel"),
                    deliveries_locations,
                )
                if odd:

                    odd = list(odd)
                    x = odd[0].get("location_x")
                    y = odd[0].get("location_y")

                _visit.update({"lattitude": y, "longitude": x})
                _visits.append(_visit)
            obj.update({"visits": _visits})
            info_for_marker.append(obj)

    return info_for_marker


def mark_in_map(map, y, x, tag, color, order=0, main_point=False):
    height = "30"
    width = "30"
    color = color
    fill_text = "black"
    text = tag
    if main_point:
        height = "30"
        width = "40"
        color = "rgb(255, 63, 80)"
        text = "Taller"
    div = folium.DivIcon(
        html=(
            f'<svg height={height} width={width} style="background-color:{color}; border-radius:4px; border: 1px outset black;" >'
            f"""
            <text x="5" y="10" fill={fill_text}>
                {f'<tspan x="5" dy="10px" >{text}</tspan>' if main_point else ""}
                {f'<tspan x="10" dy="10px" >{order}</tspan>' if order else ""}
            </text>
                
            """
            "</svg>"
        )
    )
    folium.Marker(
        [y, x],
        popup=tag + "\n" + str(order),
        tooltip=tag,
        icon=div,
    ).add_to(map)


def make_map(data: list):

    print(len(data))

    my_map = folium.Map(
        location=[25.665667776013077, -100.45060983468106], zoom_start=12
    )
    # Pass a string in popup parameter
    mark_in_map(
        my_map,
        25.665667776013077,
        -100.45060983468106,
        "Taller",
        "red",
        main_point=True,
    )

    for route in data:
        print(len(route.get("visits")))
        c = 0
        for delivery in route.get("visits"):

            mark_in_map(
                my_map,
                delivery.get("lattitude"),
                delivery.get("longitude"),
                delivery.get("order_id"),
                colors[int(route.get("route"))],
                order=c + 1,
            )
            c += 1

    my_map.save("routes.html")
