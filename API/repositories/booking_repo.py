from schemas.booking_schema import BookingCreate, BookingUpdate
from datetime import datetime, timedelta
import uuid
from supabase_client import supabase

def get_bookings():
    return supabase.table("bookings").select("*").execute().data

def get_booking_by_id(idBooking: str):
    return supabase.table("bookings").select("*").eq("idbooking", idBooking).limit(1).execute().data

def get_bookings_by_idplace(idPlace: str):
    return supabase.table("bookings").select("*").eq("idplace", idPlace).execute().data

def get_bookings_by_date(time: datetime):
    endTime = time + timedelta(milliseconds=999)
    return supabase.table("bookings").select("*").gte("date", time).lte("date", endTime).execute().data

def get_bookings_by_status(status: int):
    return supabase.table("bookings").select("*").eq("status", status).execute().data

def get_owner_ids_of_booking(idBooking: str):
    response = supabase.table("detailbookings").select("iduser").eq("idbooking", idBooking).execute().data
    
    return [user["iduser"] for user in response]
        
def get_place_id_of_booking(idBooking: str):
    response = supabase.table("bookings").select("idplace").eq("idbooking", idBooking).execute().data[0]
    
    return response["idplace"]

def create_booking(booking: BookingCreate):
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
    # Cập nhật các trường
    update_data = booking_update.model_dump(exclude_unset=True)
    if "date" in update_data:
        update_data["date"] = booking_update.date.isoformat()
    response = supabase.table("bookings").update(update_data).eq("idbooking", id_booking).execute()
    
    return response.data[0]

def delete_booking(id_booking: str):
    supabase.table("bookings").delete().eq("idbooking", id_booking).execute()
    
    return {"message": "Booking deleted successfully"}