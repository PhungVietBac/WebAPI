from fastapi import Depends, APIRouter, HTTPException, status
from schemas import detail_booking_schema
from repositories import detail_booking_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/detail_bookings/", response_model=list[detail_booking_schema.DetailBookingResponse])
def get_detail_bookings(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return detail_booking_repo.get_detail_bookings()

@router.get("detail_bookings/{select}", response_model=list[detail_booking_schema.DetailBookingResponse])
def get_detail_booking_by(select: str, lookup: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    detail_booking = detail_booking_repo.get_detail_booking_by(select, lookup)
    if not detail_booking:
        raise HTTPException(status_code=404, detail="Detail booking not found")
    
    return detail_booking

@router.get("/detail_bookings/full", response_model=detail_booking_schema.DetailBookingResponse)
def get_detail_booking_by_user_booking(idUser: str, idBooking: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    detail_booking = detail_booking_repo.get_detail_booking_by_user_booking(idUser=idUser, idBooking=idBooking)
    if not detail_booking:
        raise HTTPException(status_code=404, detail="Detail booking not found")
    
    return detail_booking[0]

@router.post("/detail_bookings/", response_model=detail_booking_schema.DetailBookingResponse)
def create_detail_booking(detail_booking: detail_booking_schema.DetailBookingCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return detail_booking_repo.create_detail_booking(detail_booking)

@router.delete("/detail_bookings", response_model=dict[str, str])
def delete_detail_booking(idUser: str, idBooking: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return detail_booking_repo.delete_detail_booking(idUser=idUser, idBooking=idBooking)
