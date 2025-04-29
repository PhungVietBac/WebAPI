from fastapi import APIRouter, Depends, HTTPException, status
from schemas import trip_schema, user_schema, place_schema
from repositories import trip_repo, user_repo, place_repo
from controllers.auth_ctrl import require_role
from datetime import datetime
from controllers.place_ctrl import parse_place

router = APIRouter()

def assert_owner_or_admin_on_trip(idTrip, current_user):
    owner_ids = trip_repo.get_members_of_trip(idTrip)
    
    if current_user["role"] != 0 and current_user["iduser"] not in owner_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return owner_ids

# Post a new trip
@router.post("/trips/", response_model=trip_schema.TripResponse)
def create_trip(trip: trip_schema.TripCreate, current_user = Depends(require_role([0, 1]))):
    return trip_repo.create_trip(trip=trip)

# Get all trips
@router.get("/trips/", response_model=list[trip_schema.TripResponse])
def get_trips(current_user = Depends(require_role([0, 1]))):
    return trip_repo.get_trips()

# Get a trip by id
@router.get("/trips", response_model=trip_schema.TripResponse)
def get_trip_by_id(idTrip: str, current_user = Depends(require_role([0, 1]))):
    trip = trip_repo.get_trip_by_id(idTrip=idTrip)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    return trip[0]

# Get a trip by
@router.get("/trips/{select}", response_model=list[trip_schema.TripResponse])
def get_trip_by(select: str, lookup: str, current_user = Depends(require_role([0, 1]))):
    if select == "startDate":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        trip = trip_repo.get_trips_by_start_date(time)
    elif select == "endDate":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        trip = trip_repo.get_trips_by_end_date(time)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
    
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    return trip

# Get trips by date and keyword
@router.get("/trips/date-key/", response_model=list[trip_schema.TripResponse])
def get_trips_date_key(start_date: str = None, end_date: str = None, keyword: str = None, current_user = Depends(require_role([0, 1]))):
    if start_date and end_date:
        try:
            time_start = datetime.strptime(start_date, "%d/%m/%Y %H:%M:%S")
            time_end = datetime.strptime(end_date, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        trip = trip_repo.get_trips_by_date_range(time_start, time_end)
    # Lọc theo tên chuyến đi
    elif keyword:
        trip = trip_repo.get_trips_by_keyword(keyword)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    return trip

# Get members by trip
@router.get("/trips/{idTrip}/members/", response_model=list[user_schema.UserResponse])
def get_members_by_trip(idTrip: str = None, current_user = Depends(require_role([0, 1]))):
    return trip_repo.get_members_of_trip(idTrip)

@router.get("/trips/{idTrip}/reviewed/", response_model=list[user_schema.UserResponse])
def get_users_reviewed_trip(idTrip: str = None, current_user = Depends(require_role([0, 1]))):
    if not trip_repo.get_trip_by_id(idTrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    user_ids = trip_repo.get_users_reviewed_trip(idTrip)
    
    if not user_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users reviewed this trip")
    
    return [user_repo.get_user_by("idUser", user_id)[0] for user_id in user_ids]

@router.get("/trips/{idTrip}/places/", response_model=list[place_schema.PlaceResponse])
def get_places_of_trip(idTrip: str = None, current_user = Depends(require_role([0, 1]))):
    if not trip_repo.get_trip_by_id(idTrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    place_ids = trip_repo.get_places_of_trip(idTrip)
    
    if not place_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No places found for this trip")
    
    return [parse_place(place_repo.get_place_by_id(place_id)[0]) for place_id in place_ids]

# Update a trip
@router.put("/trips/{idTrip}", response_model=trip_schema.TripResponse)
def update_trip(idTrip: str, trip: trip_schema.TripUpdate, current_user = Depends(require_role([0, 1]))):
    if not trip_repo.get_trip_by_id(idTrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    assert_owner_or_admin_on_trip(idTrip, current_user)
    
    return trip_repo.update_trip(idTrip, trip)

# Delete a trip
@router.delete("/trips/{idTrip}", response_model=dict[str, str])
def delete_trip(idTrip: str, current_user = Depends(require_role([0, 1]))):
    if not trip_repo.get_trip_by_id(idTrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    assert_owner_or_admin_on_trip(idTrip, current_user)
    
    return trip_repo.delete_trip(idTrip)