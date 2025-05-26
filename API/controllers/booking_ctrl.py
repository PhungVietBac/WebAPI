from fastapi import APIRouter, Depends, HTTPException, status
from schemas.booking_schema import BookingCreate, BookingUpdate, BookingResponse
from schemas.user_schema import UserResponse
from schemas.place_schema import PlaceResponse
from repositories import booking_repo, user_repo, place_repo
from controllers.auth_ctrl import require_role
from datetime import datetime
from controllers.place_ctrl import parse_place

router = APIRouter()

def assert_owner_or_admin_on_booking(id_booking: str, current_user):
    owner_ids = booking_repo.get_owner_ids_of_booking(id_booking)

    if current_user["role"] != 0 and current_user["iduser"] not in owner_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return owner_ids

@router.get("/bookings/", response_model=list[BookingResponse])
def get_bookings(current_user = Depends(require_role([0]))):
    return booking_repo.get_bookings()

@router.get("/bookings", response_model=BookingResponse)
def get_booking_by_id(idBooking: str, current_user = Depends(require_role([0, 1]))):
    booking = booking_repo.get_booking_by_id(idBooking)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    assert_owner_or_admin_on_booking(idBooking, current_user)
    
    return booking[0]

@router.get("/bookings/{select}", response_model=list[BookingResponse], summary="Get booking by idPlace, date, status")
def get_booking_by(select: str, lookup: str, current_user = Depends(require_role([0, 1]))):
    if select == "idPlace":
        bookings = booking_repo.get_bookings_by_idplace(lookup)
    elif select == "date":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        bookings = booking_repo.get_bookings_by_date(time)
    elif select == "status": 
        try:
            value = int(lookup)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        bookings = booking_repo.get_bookings_by_status(value)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid select parameter")

    if current_user["role"] != 0:
        bookings = [
            b for b in bookings
            if current_user["iduser"] in booking_repo.get_owner_ids_of_booking(b["idbooking"])
        ]
    
    if not bookings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    return bookings

@router.get("/bookings/{idBooking}/users/", response_model=list[UserResponse])
def get_owners_of_booking(idBooking: str, current_user = Depends(require_role([0, 1]))):
    if not booking_repo.get_booking_by_id(idBooking):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    user_ids = assert_owner_or_admin_on_booking(idBooking, current_user)

    return [user_repo.get_user_by_id(user_id)[0] for user_id in user_ids]

@router.get("/bookings/{idBooking}/places/", response_model=PlaceResponse)
def get_place_by_booking(idBooking: str, current_user = Depends(require_role([0, 1]))):
    if not get_booking_by_id(idBooking):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    assert_owner_or_admin_on_booking(idBooking, current_user)
    
    place_id = booking_repo.get_place_id_of_booking(idBooking)
    
    return parse_place(place_repo.get_place_by_id(place_id)[0])

@router.post("/bookings/", response_model=BookingResponse)
def create_new_booking(booking: BookingCreate, current_user = Depends(require_role([0, 1]))):
    # Kiểm tra idPlace
    if not place_repo.get_place_by_id(booking.idplace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")

    # Tạo booking nếu kiểm tra thành công
    return booking_repo.create_booking(booking)

@router.put("/bookings/", response_model=BookingResponse)
def update_booking(idBooking: str, booking: BookingUpdate, current_user = Depends(require_role([0, 1]))):
    if not get_booking_by_id(idBooking):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    assert_owner_or_admin_on_booking(idBooking, current_user)
    
    # Kiểm tra idPlace
    if not place_repo.get_place_by_id(booking.idplace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    return booking_repo.update_booking(idBooking, booking)

@router.delete("/bookings/", response_model=dict[str, str])
def delete_booking(id_booking: str, current_user = Depends(require_role([0, 1]))):
    if not get_booking_by_id(id_booking):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    assert_owner_or_admin_on_booking(id_booking, current_user)
    
    return booking_repo.delete_booking(id_booking)