from schemas.booking_schema import BookingCreate, BookingUpdate
from datetime import datetime, timedelta
from fastapi import HTTPException
from repositories import place_repo
import uuid
from supabase_client import supabase

def get_bookings():
    return supabase.table("bookings").select("*").execute().data

def get_booking_by_id(idBooking: str):
    return supabase.table("bookings").select("*").eq("idbooking", idBooking).execute().data

def get_booking_by(select: str, lookup: str):
    if select == "idPlace":
        return supabase.table("bookings").select("*").eq("idplace", lookup).execute().data
    elif select == "date":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(400, "Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        endTime = time + timedelta(milliseconds=999)
        return supabase.table("bookings").select("*").gte("date", time).lte("date", endTime).execute().data
    elif select == "status":
        try:
            value = int(lookup)
        except ValueError:
            raise HTTPException(400, "Invalid status")
        return supabase.table("bookings").select("*").eq("status", value).execute().data
    else:
        raise HTTPException(400, "Bad Request")
    
def get_owners_of_booking(idBooking: str):
    booking = get_booking_by_id(idBooking)
    if not booking:
        raise HTTPException(404, "Booking not found")
    
    response = supabase.table("detailbookings").select("iduser").eq("idbooking", idBooking).execute().data
    
    user_ids = [user["iduser"] for user in response]
    if not user_ids:
        raise HTTPException(404, "Booking hasn't any owners")
    
    return supabase.table("users").select("*").in_("iduser", user_ids).execute().data
        
def get_place_of_booking(idBooking: str):
    booking = get_booking_by_id(idBooking)
    if not booking:
        raise HTTPException(404, "Booking not found")
    
    response = supabase.table("bookings").select("idplace").eq("idbooking", idBooking).execute().data
    
    place_ids = [place["idplace"] for place in response]
    
    if not place_ids:
        raise HTTPException(404, "This booking hasn't any places")
    
    return supabase.table("places").select("*").in_("idplace", place_ids).execute().data[0]

def create_booking(booking: BookingCreate):
    # Kiểm tra idPlace
    if not place_repo.get_place_by_id(booking.idplace):
        raise HTTPException(status_code=404, detail="Place not found")
    
    id_booking = ""
    while not id_booking or get_booking_by_id(id_booking):
        id_booking = f"BK{str(uuid.uuid4())[:4]}"
        
    date_str = booking.date.isoformat()
        
    # Tạo đối tượng Booking từ dữ liệu đầu vào
    db_booking = {
        "idbooking": id_booking,
        "idplace": booking.idplace,
        "date": date_str,
        "status": booking.status
    }
    
    response = supabase.table("bookings").insert(db_booking).execute()
    
    return response.data[0]

def update_booking(id_booking: str, booking_update: BookingUpdate):
    # Cập nhật booking nếu kiểm tra thành công    
    if not get_booking_by_id(id_booking):
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Kiểm tra idPlace
    if not place_repo.get_place_by_id(booking_update.idplace):
        raise HTTPException(status_code=404, detail="Place not found")

    # Cập nhật các trường
    update_data = booking_update.model_dump(exclude_unset=True)
    if "date" in update_data:
        update_data["date"] = booking_update.date.isoformat()
    response = supabase.table("bookings").update(update_data).eq("idbooking", id_booking).execute()
    
    return response.data[0]

def delete_booking(id_booking: str):
    # Xóa booking nếu kiểm tra thành công    
    if not get_booking_by_id(id_booking):
        raise HTTPException(status_code=404, detail="Booking not found")
    
    supabase.table("bookings").delete().eq("idbooking", id_booking).execute()
    
    return {"message": "Booking deleted successfully"}