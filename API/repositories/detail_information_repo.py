from schemas.detail_information_schema import DetailCreate, DetailUpdate
import uuid
from datetime import datetime, timedelta
from supabase_client import supabase

def get_details(skip: int, limit: int):
    return supabase.table("detailinformations").select("*").range(skip, skip + limit - 1).execute().data

# Get detail information by id
def get_detail_information_by_id(id: str):
    return supabase.table("detailinformations").select("*").eq("iddetail", id).limit(1).execute().data
    
def get_detail_by_idPlace(idPlace: str, skip: int, limit: int):
    return supabase.table("detailinformations").select("*").eq("idplace", idPlace).range(skip, skip + limit - 1).execute().data

def get_detail_by_idTrip(idTrip: str, skip: int, limit: int):
    return supabase.table("detailinformations").select("*").eq("idtrip", idTrip).range(skip, skip + limit - 1).execute().data

def get_detail_by_startTime(time: datetime, skip: int, limit: int):
    endTime = time + timedelta(milliseconds=999)
    return supabase.table("detailinformations").select("*").gte("starttime", time).lte("starttime", endTime).range(skip, skip + limit - 1).execute().data

def get_detail_by_endTime(time: datetime, skip: int, limit: int):
    endTime = time + timedelta(milliseconds=999)
    return supabase.table("detailinformations").select("*").gte("endtime", time).lte("endtime", endTime).range(skip, skip + limit - 1).execute().data
    
def post_detail_information(detail: DetailCreate):
    idDetail = ""
    while not idDetail or get_detail_information_by_id(idDetail):
        idDetail = f"DI{str(uuid.uuid4())[:4]}"
        
    start_time_str = detail.starttime.isoformat()
    end_time_str = detail.endtime.isoformat()    
    
    new_detail = {
        "iddetail": idDetail,
        "idplace": detail.idplace,
        "idtrip": detail.idtrip,
        "starttime": start_time_str,
        "endtime": end_time_str,
        "note": detail.note
    }
    
    response = supabase.table("detailinformations").insert(new_detail).execute()
    return response.data[0]

# Update detail information
def update_detail_information(id: str, detail: DetailUpdate):
    update_data = detail.model_dump(exclude_unset=True)
    if "starttime" in update_data:
        update_data["starttime"] = detail.starttime.isoformat()
    if "endtime" in  update_data:
        update_data["endtime"] = detail.endtime.isoformat()
    
    response = supabase.table("detailinformations").update(update_data).eq("iddetail", id).execute()
    return response.data[0]

# Delete detail information
def delete_detail_information(id: str):
    supabase.table("detailinformations").delete().eq("iddetail", id).execute()
    return {"message": "Detail information deleted successfully"}
