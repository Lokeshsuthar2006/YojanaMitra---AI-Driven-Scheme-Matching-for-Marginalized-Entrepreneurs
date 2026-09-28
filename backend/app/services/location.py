from math import asin, cos, radians, sin, sqrt


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return round(2 * 6371 * asin(sqrt(a)), 2)


def partner_sort_key(partner: dict) -> tuple:
    """Keep a genuine 0 km result ahead of records without coordinates."""
    distance = partner.get("distance_km")
    return (distance is None, distance if distance is not None else float("inf"), not partner.get("local_match", False))
