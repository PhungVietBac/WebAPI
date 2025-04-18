from schemas.place_schema import PlaceCreate, PlaceUpdate
from fastapi import HTTPException
import uuid
from supabase_client import supabase

def get_places(skip: int, limit: int):
    return supabase.table("places").select("*").range(skip, skip + limit - 1).execute().data

# Get place by id
def get_place_by_id(id: str):
    return supabase.table("places").select("*").eq("idplace", id).execute().data

def get_place_by(select: str, lookup: str):
    if select == "name":
        return supabase.table("places").select("*").eq("name", lookup).execute().data
    elif select == "country":
        return supabase.table("places").select("*").eq("country", lookup).execute().data
    elif select == "city":
        return supabase.table("places").select("*").eq("city", lookup).execute().data
    elif select == "province":
        return supabase.table("places").select("*").eq("province", lookup).execute().data
    elif select == "type":
        try:
            value = int(lookup)
        except ValueError:
            raise HTTPException(400, "Invalid type")
        return supabase.table("places").select("*").eq("type", value).execute().data
    elif select == "rating":
        try:
            value = float(lookup)
        except ValueError:
            raise HTTPException(400, "Invalid rating")
        return supabase.table("places").select("*").eq("rating", value).execute().data
    else:
        raise HTTPException(400, "Bad Request")

def get_bookings_of_place(idPlace: str):
    place = get_place_by_id(idPlace)
    if not place:
        raise HTTPException(404, "Place not found")
    
    response = supabase.table("bookings").select("*").eq("idplace", idPlace).execute().data
    
    if not response:
        raise HTTPException(404, "Place hasn't ever booked")
    
    return response
        
def get_trips_contain_place(idPlace: str):
    place = get_place_by_id(idPlace)
    if not place:
        raise HTTPException(404, "Place not found")
    
    response = supabase.table("detailinformations").select("idtrip").eq("idplace", idPlace).execute().data
    trip_ids = [trip["idtrip"] for trip in response]
    
    if not trip_ids:
        raise HTTPException(404, "Place hasn't ever booked")
    
    return supabase.table("trips").select("*").in_("idtrip", trip_ids).execute().data

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

# Post place
def post_place(place: PlaceCreate):
    idPlace = ""
    while not idPlace or get_place_by_id(idPlace):
        idPlace = f"PL{str(uuid.uuid4())[:4]}"
    
    new_place = {
        "idplace": idPlace,
        "name": place.name,
        "country": place.country,
        "city": place.city,
        "province": place.province,
        "address": place.address,
        "description": place.description,
        "rating": place.rating,
        "type": place.type
    }
    
    response = supabase.table("places").insert(new_place).execute()
    return response.data[0]

# Update place
def update_place(id: str, place: PlaceUpdate):
    # Check if IDPlace exists
    db_place = get_place_by_id(id)
    if not db_place:
        raise HTTPException(404, "Place not found")
    
    update_data = {key: value for key, value in place.model_dump(exclude_unset=True).items()}
    
    response = supabase.table("places").update(update_data).eq("idplace", id).execute()
    return response.data[0]

def delete_place(idPlace: str):
    db_place = get_place_by_id(idPlace)
    if not db_place:
       raise HTTPException(status_code=404, detail="Place not found")
    
    supabase.table("places").delete().eq("idplace", idPlace).execute()
    return {"message": "Place deleted successfully"}
