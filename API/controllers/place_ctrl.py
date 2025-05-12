from fastapi import APIRouter, Depends, HTTPException, status
from schemas import place_schema, booking_schema, trip_schema
from controllers.auth_ctrl import require_role
from repositories import place_repo, trip_repo
from shapely import wkb
from shapely.geometry import Point
import binascii

router = APIRouter()

def parse_wkb(wkb_data: str):
    wkb_bytes = binascii.unhexlify(wkb_data)
    point = wkb.loads(wkb_bytes)
    lat, lon = point.y, point.x
    return lat, lon

def parse_lat_lon(lat: float, lon: float):
    point = Point(lon, lat)
    wkb_data = wkb.dumps(point)
    return binascii.hexlify(wkb_data).decode()

def parse_place(place):
    lat, lon = parse_wkb(place["loc"])
    return {
        "idplace": place["idplace"],
        "name": place["name"],
        "country": place["country"],
        "city": place["city"],
        "province": place["province"],
        "address": place["address"],
        "description": place["description"],
        "rating": place["rating"],
        "type": place["type"],
        "lat": lat,
        "lon": lon
    }

def parse_response(res):
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    if len(res) == 1:
        return parse_place(res[0])
    
    result = []
    for item in res:
        result.append(parse_place(item))
    return result

@router.get("/places/all", response_model=list[place_schema.PlaceResponse])
def get_places(current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    res = place_repo.get_places(skip, limit)
    
    return parse_response(res)

@router.get("/places", response_model=place_schema.PlaceResponse)
def get_place_by_id(idPlace: str, current_user = Depends(require_role([0, 1]))):
    place = place_repo.get_place_by_id(idPlace)
    print(place)
    
    return parse_response(place)

@router.get("/places/{idPlace}/bookings/", response_model=list[booking_schema.BookingResponse])
def get_bookings_by_place(idPlace: str, current_user = Depends(require_role([0]))):
    if not place_repo.get_place_by_id(idPlace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    response = place_repo.get_bookings_of_place(idPlace)
    
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place hasn't ever booked")
    
    return response

@router.get("/places/{select}", response_model=list[place_schema.PlaceResponse], summary="Get place by name, country, city, province, type, rating")
def get_place_by(select: str, lookup: str, current_user = Depends(require_role([0, 1]))):
    if select == "name":
        places = place_repo.get_place_by_name(lookup)
    elif select == "country":
        places = place_repo.get_place_by_country(lookup)
    elif select == "city":
        places = place_repo.get_place_by_city(lookup)
    elif select == "province":
        places = place_repo.get_place_by_province(lookup)
    elif select == "type":
        try:
            value = int(lookup)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid type")
        places = place_repo.get_place_by_type(value)
    elif select == "rating":
        try:
            value = float(lookup)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rating")
        places = place_repo.get_place_by_rating(value)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
    
    return parse_response(places)

@router.get("/places/{idPlace}/trips/", response_model=list[trip_schema.TripResponse])
def get_trips_by_place(idPlace: str, current_user = Depends(require_role([0, 1]))):
    if not place_repo.get_place_by_id(idPlace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    trip_ids = place_repo.get_trip_ids_contain_place(idPlace)
    if not trip_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No any trip found")
    
    return [trip_repo.get_trip_by_id(trip_id)[0] for trip_id in trip_ids]

@router.get("/search/", response_model=list[place_schema.PlaceResponse])
def search_places(
    query: str,
    place_type: int = None,
    min_rating: int = None,
    current_user = Depends(require_role([0, 1]))
):
    """Search places with filters"""
    places = place_repo.search_places(
        query=query,
        place_type=place_type,
        min_rating=min_rating
    )
    
    return parse_response(places)

@router.get("/loc/{lat}&{lon}",response_model=place_schema.PlaceResponse)
def get_place_by_loc(lat: float, lon: float, current_user = Depends(require_role([0, 1]))):
    loc = parse_lat_lon(lat, lon)
    place = place_repo.get_place_by_lat_lon(loc)
    
    return parse_response(place)

@router.post("/places/", response_model=place_schema.PlaceResponse)
def create_place(place: place_schema.PlaceCreate, current_user = Depends(require_role([0, 1]))):
    
    return parse_place(place_repo.post_place(place))

@router.put("/places/{idPlace}", response_model=place_schema.PlaceResponse)
def update_place(idPlace: str, place: place_schema.PlaceUpdate, current_user = Depends(require_role([0]))):
    if not place_repo.get_place_by_id(idPlace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    return parse_place(place_repo.update_place(idPlace, place))

@router.delete("/places/{idPlace}", response_model=dict[str, str])
def delete_place(idPlace: str, current_user = Depends(require_role([0]))):
    if not place_repo.get_place_by_id(idPlace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    return place_repo.delete_place(idPlace)
