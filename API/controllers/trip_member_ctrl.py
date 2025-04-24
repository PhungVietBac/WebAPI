from fastapi import Depends, APIRouter, HTTPException, status
from schemas import trip_member_schema
from repositories import trip_member_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

# Get all trip_members
@router.get("/trip_members/", response_model=list[trip_member_schema.TripMemberResponse])
def get_trip_members(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return trip_member_repo.get_trip_members()

# Get a trip_member by
@router.get("/trip_members/{select}", response_model=list[trip_member_schema.TripMemberResponse])
def get_trip_member_by(select: str, lookup: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    trip_member = trip_member_repo.get_trip_member_by(select=select, lookup=lookup)
    if not trip_member:
        raise HTTPException(status_code=404, detail="Trip member not found")
    
    return trip_member

# Get a trip_member by user and trip
@router.get("/trip_members/full/", response_model=trip_member_schema.TripMemberResponse)
def get_trip_member_by_user_trip(idUser: str, idTrip: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    trip_member = trip_member_repo.get_trip_member_by_user_trip(idUser=idUser, idTrip=idTrip)
    if not trip_member:
        raise HTTPException(status_code=404, detail="Trip member not found")
    
    return trip_member[0]

# Post a new trip_member
@router.post("/trip_members/", response_model=trip_member_schema.TripMemberResponse)
def create_trip_member(trip_member: trip_member_schema.TripMemberCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return trip_member_repo.create_trip_member(trip_member=trip_member)

# Delete a trip_member
@router.delete("/trip_members", response_model=dict[str, str])
def delete_trip_member(idUser: str, idTrip: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return trip_member_repo.delete_trip_member(idUser=idUser, idTrip=idTrip)
