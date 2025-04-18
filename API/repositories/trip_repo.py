from supabase_client import supabase
from schemas.trip_schema import TripCreate, TripUpdate
from datetime import datetime, timedelta
from fastapi import HTTPException
import uuid

#tìm trong start_date -> end_date và theo keyword
def get_trips(start_date: str = None, end_date: str = None, keyword: str = None):
    query = supabase.table("trips").select("*")
    
    # Lọc theo ngày bắt đầu và kết thúc
    if start_date and end_date:
        try:
            time_start = datetime.strptime(start_date, "%d/%m/%Y %H:%M:%S")
            time_end = datetime.strptime(end_date, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        query = query.filter("startdate", "gte", time_start).filter("enddate", "lte", time_end)
    
    # Lọc theo tên chuyến đi
    elif keyword:
        query = query.ilike("name", f"%{keyword}%")
    
    else:
        raise HTTPException(status_code=400, detail="Bad Request")
    
    return query.execute().data

# Get a trip by id
def get_trip_by_id(idTrip: str):
    return supabase.table("trips").select("*").eq("idtrip", idTrip).execute().data

# Get a trip by
def get_trip_by(select: str, lookup: str):
    if select == "startDate":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        endTime = time + timedelta(milliseconds=999)
        return supabase.table("trips").select("*").filter("startdate", "gte", time).filter("startdate", "lte", endTime).execute().data
    elif select == "endDate":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        endTime = time + timedelta(milliseconds=999)
        return supabase.table("trips").select("*").filter("enddate", "gte", time).filter("enddate", "lte", endTime).execute().data
    else:
        raise HTTPException(status_code=400, detail="Bad Request")

def get_members_of_trip(idTrip: str):
    trip = get_trip_by_id(idTrip)
    if not trip:
        raise HTTPException(404, "Trip not found")
    
    response = supabase.table("tripmembers").select("iduser").eq("idtrip", idTrip).execute().data
    member_ids = [member["iduser"] for member in response]
    
    if not member_ids:
        raise HTTPException(404, "No members found for this trip")
    
    return supabase.table("users").select("*").in_("iduser", member_ids).execute().data


def get_users_reviewed_trip(idTrip: str):
    trip = get_trip_by_id(idTrip)
    if not trip:
        raise HTTPException(404, "Trip not found")
    
    response = supabase.table("reviews").select("iduser").eq("idtrip", idTrip).execute().data
    user_ids = [user["iduser"] for user in response]
    
    if not user_ids:
        raise HTTPException(404, "No users reviewed this trip")
    
    return supabase.table("users").select("*").in_("iduser", user_ids).execute().data


def get_places_of_trip(idTrip: str):
    trip = get_trip_by_id(idTrip)
    if not trip:
        raise HTTPException(404, "Trip not found")
    
    response = supabase.table("detailinformations").select("idplace").eq("idtrip", idTrip).execute().data
    place_ids = [place["idplace"] for place in response]
    
    if not place_ids:
        raise HTTPException(404, "No places found for this trip")
    
    return supabase.table("places").select("*").in_("idplace", place_ids).execute().data

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
    existing_trip = get_trip_by_id(idTrip)
    if not existing_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
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
    db_trip = get_trip_by_id(idTrip)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    response = supabase.table("trips").delete().eq("idtrip", idTrip).execute()
    return {"message": "Trip deleted successfully"}
