from schemas.detail_information_schema import DetailCreate, DetailUpdate
import uuid
from repositories import place_repo, trip_repo
from fastapi import HTTPException
from datetime import datetime, timedelta
from supabase_client import supabase

def get_details(skip: int, limit: int):
    return supabase.table("detailinformations").select("*").range(skip, skip + limit - 1).execute().data

# Get detail information by id
def get_detail_information_by_id(id: str):
    return supabase.table("detailinformations").select("*").eq("iddetail", id).execute().data

def get_detail_by(select: str, lookup: str, skip: int, limit: int):
    if select == "idPlace":
        return supabase.table("detailinformations").select("*").eq("idplace", lookup).range(skip, skip + limit - 1).execute().data
    elif select == "idTrip":
        return supabase.table("detailinformations").select("*").eq("idtrip", lookup).range(skip, skip + limit - 1).execute().data
    elif select == "startTime":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(400, "Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        endTime = time + timedelta(milliseconds=999)
        return supabase.table("detailinformations").select("*").gte("starttime", time).lte("starttime", endTime).range(skip, skip + limit - 1).execute().data
    elif select == "endTime":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(400, "Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        endTime = time + timedelta(milliseconds=999)
        return supabase.table("detailinformations").select("*").gte("endtime", time).lte("endtime", endTime).range(skip, skip + limit - 1).execute().data
    else:
        raise HTTPException(400, "Bad Request")

# Post detail information
def post_detail_information(detail: DetailCreate):
    if not place_repo.get_place_by_id(detail.idplace):
        raise HTTPException(404, "Place not found")
    
    if not trip_repo.get_trip_by_id(detail.idtrip):
        raise HTTPException(404, "Trip not found")
    
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
    if not place_repo.get_place_by_id(detail.idplace):
        raise HTTPException(404, "Place not found")
    
    if not trip_repo.get_trip_by_id(detail.idtrip):
        raise HTTPException(404, "Trip not found")
    
    db_detail = get_detail_information_by_id(id)
    if not db_detail:
        raise HTTPException(404, "Detail information not found")
     
    update_data = detail.model_dump(exclude_unset=True)
    if "starttime" in update_data:
        update_data["starttime"] = detail.starttime.isoformat()
    if "endtime" in  update_data:
        update_data["endtime"] = detail.endtime.isoformat()
    
    response = supabase.table("detailinformations").update(update_data).eq("iddetail", id).execute()
    return response.data[0]

# Delete detail information
def delete_detail_information(id: str):
    # Check if IDDetail exists
    db_detail = get_detail_information_by_id(id)
    if not db_detail:
        raise HTTPException(404, "Detail information not found")
    
    supabase.table("detailinformations").delete().eq("iddetail", id).execute()
    return {"message": "Detail information deleted successfully"}
