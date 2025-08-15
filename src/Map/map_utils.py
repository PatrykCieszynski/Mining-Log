from typing import Tuple, Dict, Any, cast


def get_planet_config(config: Dict[str, Any]) -> Dict[str, Any]:
    current_planet = config["map"]["planet"]
    return cast(Dict[str, Any], config["planets"][current_planet])


def coord_to_pixel_radius(config: Dict[str, Any]) -> int:
    planet_config = get_planet_config(config)
    tile_size = config["map"]["tile_size"]
    radius_coord = config["player"]["radius_coord"]
    map_width = planet_config["tile_count_x"] * tile_size
    lon_range = planet_config["max_lon"] - planet_config["min_lon"]
    if lon_range == 0:
        print("Error: Longitude range is zero.")
        return 0
    print("coord_to_pixel_radius output: ", int((radius_coord / lon_range) * map_width))
    return int((radius_coord / lon_range) * map_width)


def lonlat_to_scene(lon: float, lat: float, config: Dict[str, Any]) -> Tuple[int, int]:
    planet_config = get_planet_config(config)
    tile_size = config["map"]["tile_size"]
    map_width = planet_config["tile_count_x"] * tile_size
    map_height = planet_config["tile_count_y"] * tile_size
    x = (
                (lon - planet_config["min_lon"])
                / (planet_config["max_lon"] - planet_config["min_lon"])
        ) * map_width
    y = (
            map_height
            - (
                    (lat - planet_config["min_lat"])
                    / (planet_config["max_lat"] - planet_config["min_lat"])
            )
            * map_height
    )
    print("lonlat_to_Scene output: ", x, y)
    return x, y
