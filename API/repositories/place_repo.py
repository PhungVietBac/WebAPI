from supabase_client import supabase
from schemas.place_schema import PlaceCreate, PlaceUpdate
import uuid

def get_places(skip: int, limit: int):
    return supabase.table("places").select("*").range(skip, skip + limit - 1).execute().data

# Get place by id
def get_place_by_id(id: str):
    return supabase.table("places").select("*").eq("idplace", id).limit(1).execute().data

def get_place_by_name(name: str):
    return supabase.table("places").select("*").eq("name", name).execute().data

def get_place_by_country(country: str):
    return supabase.table("places").select("*").eq("country", country).execute().data

def get_place_by_city(city: str):
    return supabase.table("places").select("*").eq("city", city).execute().data

def get_place_by_province(province: str):
    return supabase.table("places").select("*").eq("province", province).execute().data

def get_place_by_type(type: int):
    return supabase.table("places").select("*").eq("type", type).execute().data

def get_place_by_rating(rating: float):
    return supabase.table("places").select("*").eq("rating", rating).execute().data

def get_bookings_of_place(idPlace: str):
    return supabase.table("bookings").select("*").eq("idplace", idPlace).execute().data
        
def get_trip_ids_contain_place(idPlace: str):
    response = supabase.table("detailinformations").select("idtrip").eq("idplace", idPlace).execute().data
    return [trip["idtrip"] for trip in response]

def search_places(query: str, place_type: int = None, min_rating: int = None):
    or_filter = (
        f"name.ilike.*{query}*,"
        f"city.ilike.*{query}*,"
        f"country.ilike.*{query}*,"
        f"province.ilike.*{query}*,"
        f"address.ilike.*{query}*"
    )

    q = supabase.table("places").select("*").or_(or_filter)

    # Thêm điều kiện place_type nếu có
    if not place_type:
        q = q.eq("type", place_type)
    
    # Thêm điều kiện min_rating nếu có
    if not min_rating:
        q = q.gte("rating", min_rating)

    return q.execute().data

def get_place_by_lat_lon(loc: str):
    return supabase.table("places").select("*").eq("loc", loc).execute().data

# Post place
def post_place(place: PlaceCreate):
    idPlace = ""
    while not idPlace or get_place_by_id(idPlace):
        idPlace = f"PL{str(uuid.uuid4())[:4]}"
        
    point_wkt = f"SRID=4326;POINT({place.lon} {place.lat})"
    
    new_place = {
        "idplace": idPlace,
        "name": place.name,
        "country": place.country,
        "city": place.city,
        "province": place.province,
        "address": place.address,
        "description": place.description,
        "rating": place.rating,
        "type": place.type,
        "loc": point_wkt
    }
    
    response = supabase.table("places").insert(new_place).execute()
    return response.data[0]

# Update place
def update_place(id: str, place: PlaceUpdate):
    update_data = place.model_dump(exclude={"lat", "lon"}, exclude_unset=True)
    
    if place.lat and place.lon:
        update_data["loc"] = f"SRID=4326;POINT({place.lon} {place.lat})"
    
    response = supabase.table("places").update(update_data).eq("idplace", id).execute()
    print(response)
    return response.data[0]

def delete_place(idPlace: str):
    supabase.table("places").delete().eq("idplace", idPlace).execute()
    return {"message": "Place deleted successfully"}
