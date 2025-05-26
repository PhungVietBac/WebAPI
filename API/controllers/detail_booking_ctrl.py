from fastapi import Depends, APIRouter, HTTPException, status
from schemas import detail_booking_schema
from repositories import detail_booking_repo, user_repo, booking_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin

router = APIRouter()

@router.get("/detail_bookings/", response_model=list[detail_booking_schema.DetailBookingResponse])
def get_detail_bookings(current_user = Depends(require_role([0]))):
    return detail_booking_repo.get_detail_bookings()

@router.get("detail_bookings/{select}", response_model=list[detail_booking_schema.DetailBookingResponse], summary="Get detail booking by idUser, idBooking")
def get_detail_booking_by(select: str, lookup: str, current_user = Depends(require_role([0]))):
    if select == "idUser":
        detail_booking = detail_booking_repo.get_detail_booking_by_user(lookup)
    elif select == "idBooking":
        detail_booking = detail_booking_repo.get_detail_booking_by_booking(lookup)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid selection criteria")
    
    if not detail_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail booking not found")
    
    return detail_booking

@router.get("/detail_bookings/full", response_model=detail_booking_schema.DetailBookingResponse)
def get_detail_booking_by_user_booking(idUser: str, idBooking: str, current_user = Depends(require_role([0]))):
    detail_booking = detail_booking_repo.get_detail_booking_by_user_booking(idUser=idUser, idBooking=idBooking)
    if not detail_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail booking not found")
    
    return detail_booking[0]

@router.post("/detail_bookings/", response_model=detail_booking_schema.DetailBookingResponse)
def create_detail_booking(detail_booking: detail_booking_schema.DetailBookingCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, detail_booking.iduser)
    # Check if the user exists
    if not user_repo.get_user_by_id(detail_booking.iduser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Check if the booking exists
    if not booking_repo.get_booking_by_id(detail_booking.idbooking):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    # Check if the detail_booking already exists
    if detail_booking_repo.get_detail_booking_by_user_booking(detail_booking.iduser, detail_booking.idbooking):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Detail booking already exists")
    
    return detail_booking_repo.create_detail_booking(detail_booking)

@router.delete("/detail_bookings", response_model=dict[str, str])
def delete_detail_booking(idUser: str, idBooking: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)

    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not booking_repo.get_booking_by_id(idBooking):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    return detail_booking_repo.delete_detail_booking(idUser=idUser, idBooking=idBooking)
