import folium
import random


def process_info_for_marker(info: dict, deliveries_locations: list):

    info_for_marker = []

    routes = info.get("routes")
    if routes:
        c = 0
        for i in routes:
            c += 1
            obj = {"route": c}
            _visits = []
            visits = i.get("visits")

            if visits:

                for i in visits:
                    _visit = {"order_id": i.get("visitLabel")}

                    odd = filter(
                        lambda delivery: str(dict(delivery).get("id"))
                        == i.get("visitLabel"),
                        deliveries_locations,
                    )

                    if odd:

                        odd = list(odd)

                        x = odd[0].get("latitude")

                        y = odd[0].get("longitude")

                        if odd[0].get("schedule"):

                            _visit.update({"schedule": True})

                    _visit.update({"latitude": y, "longitude": x})
                    _visits.append(_visit)
                obj.update({"visits": _visits})
                info_for_marker.append(obj)

    return info_for_marker


def mark_in_map(map, y, x, tag, color, order=0, main_point=False, special=False):
    height = "30"
    width = "30"
    color = color
    fill_text = "white"
    text = tag
    if main_point:
        height = "30"
        width = "40"
        color = "blue"
        text = "Taller"

    div = folium.DivIcon(
        html=(
            f'<svg height={height} width={width} style="background-color:{color}; border-radius:16px; border: {"3" if special else "1"}px solid {"red" if special else "black"};" >'
            f"""
            <text x="5" y="10" fill={fill_text}>
                {f'<tspan x="5" dy="10px" >{text}</tspan>' if main_point else ''}
                {f'<tspan x="10" dy="10px" >{order}</tspan>' if order else ''}
            </text>
                
            """
            "</svg>"
        )
    )
    folium.Marker(
        [x, y],
        popup=str((tag + "\n" + str(order))) if order else tag,
        tooltip=str(order) if order else "Taller",
        icon=div,
    ).add_to(map)


def get_random_color(list_colors: list):

    while True:

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rgb = f"rgb({r},{g},{b})"
        if not rgb in list_colors:
            list_colors.append(rgb)
            return rgb


def make_map(data: list):
    list_colors = []
    colors = [get_random_color(list_colors) for x in range(len(data) + 1)]

    my_map = folium.Map(
        location=[25.665667776013077, -100.45060983468106], zoom_start=12
    )
    # Pass a string in popup parameter
    mark_in_map(
        my_map,
        -100.45060983468106,
        25.665667776013077,
        "Taller",
        "red",
        main_point=True,
    )

    color_n = 0
    for route in data:
        c = 0
        for delivery in route.get("visits"):
            mark_in_map(
                my_map,
                str(delivery.get("latitude")),
                str(delivery.get("longitude")),
                delivery.get("order_id"),
                color=colors[color_n],
                order=c + 1,
                special=delivery.get("schedule"),
            )
            c += 1
        color_n += 1

    my_map.save("routes.html")
