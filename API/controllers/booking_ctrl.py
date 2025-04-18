from fastapi import APIRouter, Depends, HTTPException, status
from schemas.booking_schema import BookingCreate, BookingUpdate, BookingResponse
from schemas.user_schema import UserResponse
from schemas.place_schema import PlaceResponse
from repositories import booking_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/bookings/", response_model=list[BookingResponse])
def get_bookings(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return booking_repo.get_bookings()

@router.get("/bookings", response_model=BookingResponse)
def get_booking_by_id(idBooking: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    booking = booking_repo.get_booking_by_id(idBooking)
    if not booking:
        raise HTTPException(404, "Booking not found")
    
    return booking[0]

@router.get("/bookings/{select}", response_model=list[BookingResponse])
def get_booking_by(select: str, lookup: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    booking = booking_repo.get_booking_by(select, lookup)
    if booking == []:
        raise HTTPException(404, "Booking not found")
    
    return booking

@router.get("/bookings/{idBooking}/users/", response_model=list[UserResponse])
def get_owners_of_booking(idBooking: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return booking_repo.get_owners_of_booking(idBooking)

@router.get("/bookings/{idBooking}/places/", response_model=PlaceResponse)
def get_place_by_booking(idBooking: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return booking_repo.get_place_of_booking(idBooking)

@router.post("/bookings/", response_model=BookingResponse)
def create_new_booking(booking: BookingCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)

    # Tạo booking nếu kiểm tra thành công
    return booking_repo.create_booking(booking)

@router.put("/bookings/", response_model=BookingResponse)
def update_booking(idBooking: str, booking: BookingUpdate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return booking_repo.update_booking(idBooking, booking)

@router.delete("/bookings/", response_model=dict[str, str])
def delete_booking(id_booking: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return booking_repo.delete_booking(id_booking)