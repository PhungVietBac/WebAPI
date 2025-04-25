from supabase_client import supabase
from schemas.trip_schema import TripCreate, TripUpdate
from datetime import datetime, timedelta
import uuid

def get_trips():
    return supabase.table("trips").select("*").execute().data

def get_trips_by_date_range(start: datetime, end: datetime):
    return supabase.table("trips").select("*").gte("startdate", start).lte("enddate", end).execute().data

def get_trips_by_keyword(keyword: str):
    return supabase.table("trips").select("*").ilike("name", f"%{keyword}%").execute().data

# Get a trip by id
def get_trip_by_id(idTrip: str):
    return supabase.table("trips").select("*").eq("idtrip", idTrip).execute().data

# Get a trip by
def get_trips_by_start_date(time: datetime):
    endTime = time + timedelta(milliseconds=999)
    return supabase.table("trips").select("*").filter("startdate", "gte", time).filter("startdate", "lte", endTime).execute().data

def get_trips_by_end_date(time: datetime):
    endTime = time + timedelta(milliseconds=999)
    return supabase.table("trips").select("*").filter("enddate", "gte", time).filter("enddate", "lte", endTime).execute().data

def get_members_of_trip(idTrip: str):
    response = supabase.table("tripmembers").select("iduser").eq("idtrip", idTrip).execute().data
    return [member["iduser"] for member in response]

def get_users_reviewed_trip(idTrip: str):
    response = supabase.table("reviews").select("iduser").eq("idtrip", idTrip).execute().data
    return [user["iduser"] for user in response]


def get_places_of_trip(idTrip: str):
    response = supabase.table("detailinformations").select("idplace").eq("idtrip", idTrip).execute().data
    return [place["idplace"] for place in response]

#tạo mới trip
def create_trip(trip: TripCreate):
    idTrip = ""
    while not idTrip or get_trip_by_id(idTrip):  # Kiểm tra ID không trùng
        idTrip = f"TR{str(uuid.uuid4())[:4]}"
        
    start_date_str = trip.startdate.isoformat()
    end_date_str = trip.enddate.isoformat()
    
    # Tạo chuyến đi trong Supabase
    response = supabase.table("trips").insert({
        "idtrip": idTrip,
        "name": trip.name,
        "startdate": start_date_str,
        "enddate": end_date_str
    }).execute()

    return response.data[0]

#update
def update_trip(idTrip: str, trip_update: TripUpdate):
    # Lọc dữ liệu cập nhật từ trip_update (chỉ lấy các trường không phải None)
    updated_data = trip_update.model_dump(exclude_unset=True)
    if "startdate" in updated_data:
        updated_data["startdate"] = trip_update.startdate.isoformat()
    if "enddate" in updated_data:
        updated_data["enddate"] = trip_update.enddate.isoformat()
    
    # Cập nhật chuyến đi trong Supabase
    response = supabase.table("trips").update(updated_data).eq("idtrip", idTrip).execute()
    return response.data[0]

#del
def delete_trip(idTrip: str):
    supabase.table("trips").delete().eq("idtrip", idTrip).execute()
    return {"message": "Trip deleted successfully"}
