from schemas.detail_booking_schema import DetailBookingCreate
from repositories import user_repo
from repositories import booking_repo
from fastapi import HTTPException
from supabase_client import supabase

def get_detail_bookings():
    return supabase.table("detailbookings").select("*").execute().data

def get_detail_booking_by(select: str, lookup: str):
    if select == "idUser":
        return supabase.table("detailbookings").select("*").eq("iduser", lookup).execute().data
    elif select == "idBooking":
        return supabase.table("detailbookings").select("*").eq("idbooking", lookup).execute().data
    else:
        raise HTTPException(400, "Bad Request")
    
def get_detail_booking_by_user_booking(idUser: str, idBooking: str):
    return supabase.table("detailbookings").select("*").eq("iduser", idUser).eq("idbooking", idBooking).execute().data

def create_detail_booking(detail_booking: DetailBookingCreate):
    # Check if the user exists
    if not user_repo.get_user_by("idUser", detail_booking.iduser):
        raise HTTPException(404, "User not found")
    # Check if the booking exists
    if not booking_repo.get_booking_by_id(detail_booking.idbooking):
        raise HTTPException(404, "Booking not found")
    # Check if the detail_booking already exists
    if get_detail_booking_by_user_booking(detail_booking.iduser, detail_booking.idbooking):
        raise HTTPException(422, "Detail booking already exists")

    db_detail_booking = {
        "iduser": detail_booking.iduser,
        "idbooking": detail_booking.idbooking
    }
    
    response = supabase.table("detailbookings").insert(db_detail_booking).execute()
    return response.data[0]

def delete_detail_booking(idUser: str, idBooking: str):
    if not user_repo.get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    
    if not booking_repo.get_booking_by_id(idBooking):
        raise HTTPException(404, "Booking not found")
    
    if not get_detail_booking_by_user_booking(idUser, idBooking):
        raise HTTPException(404, "Detail booking not found")
    
    supabase.table("detailbookings").delete().eq("iduser", idUser).eq("idbooking", idBooking).execute()
    return {"message": "Detail booking deleted successfully"}