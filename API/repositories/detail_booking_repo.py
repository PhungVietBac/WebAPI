from schemas.detail_booking_schema import DetailBookingCreate
from supabase_client import supabase

def get_detail_bookings():
    return supabase.table("detailbookings").select("*").execute().data

def get_detail_booking_by_user(idUser: str):
    return supabase.table("detailbookings").select("*").eq("iduser", idUser).execute().data

def get_detail_booking_by_booking(idBooking: str):
    return supabase.table("detailbookings").select("*").eq("idbooking", idBooking).execute().data
    
def get_detail_booking_by_user_booking(idUser: str, idBooking: str):
    return supabase.table("detailbookings").select("*").eq("iduser", idUser).eq("idbooking", idBooking).limit(1).execute().data

def create_detail_booking(detail_booking: DetailBookingCreate):
    db_detail_booking = {
        "iduser": detail_booking.iduser,
        "idbooking": detail_booking.idbooking
    }
    
    response = supabase.table("detailbookings").insert(db_detail_booking).execute()
    return response.data[0]

def delete_detail_booking(idUser: str, idBooking: str):
    supabase.table("detailbookings").delete().eq("iduser", idUser).eq("idbooking", idBooking).execute()
    return {"message": "Detail booking deleted successfully"}