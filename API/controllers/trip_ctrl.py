from fastapi import APIRouter, Depends, HTTPException, status
from schemas import trip_schema, user_schema, place_schema
from repositories import trip_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authentication(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

# Post a new trip
@router.post("/trips/", response_model=trip_schema.TripResponse)
def create_trip(trip: trip_schema.TripCreate, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.create_trip(trip=trip)

# Get all trips
@router.get("/trips/", response_model=list[trip_schema.TripResponse])
def get_trips(current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.get_trips()

# Get a trip by id
@router.get("/trips", response_model=trip_schema.TripResponse)
def get_trip_by_id(idTrip: str, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    trip = trip_repo.get_trip_by_id(idTrip=idTrip)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return trip[0]

# Get a trip by
@router.get("/trips/{select}", response_model=list[trip_schema.TripResponse])
def get_trip_by(select: str, lookup: str, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    trip = trip_repo.get_trip_by(select=select, lookup=lookup)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return trip

# Get trips by date and keyword
@router.get("/trips/date-key/", response_model=list[trip_schema.TripResponse])
def get_trips_date_key(start_date: str = None, end_date: str = None, keyword: str = None, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    trip = trip_repo.get_trips(start_date, end_date, keyword)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return trip

# Get members by trip
@router.get("/trips/{idTrip}/members/", response_model=list[user_schema.UserResponse])
def get_members_by_trip(idTrip: str = None, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.get_members_of_trip(idTrip)

@router.get("/trips/{idTrip}/reviewed/", response_model=list[user_schema.UserResponse])
def get_users_reviewed_trip(idTrip: str = None, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.get_users_reviewed_trip(idTrip)

@router.get("/trips/{idTrip}/places/", response_model=list[place_schema.PlaceResponse])
def get_places_of_trip(idTrip: str = None, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.get_places_of_trip(idTrip)

# Update a trip
@router.put("/trips/{idTrip}", response_model=trip_schema.TripResponse)
def update_trip(idTrip: str, trip: trip_schema.TripUpdate, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.update_trip(idTrip, trip)

# Delete a trip
@router.delete("/trips/{idTrip}", response_model=dict[str, str])
def delete_trip(idTrip: str, current_user = Depends(get_current_user)):
    check_authentication(current_user)
    
    return trip_repo.delete_trip(idTrip)