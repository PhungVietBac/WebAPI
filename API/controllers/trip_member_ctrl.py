from fastapi import Depends, APIRouter, HTTPException, status
from schemas import trip_member_schema
from repositories import trip_member_repo, user_repo, trip_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin

router = APIRouter()

# Get all trip_members
@router.get("/trip_members/", response_model=list[trip_member_schema.TripMemberResponse])
def get_trip_members(current_user = Depends(require_role([0]))):
    return trip_member_repo.get_trip_members()

# Get a trip_member by
@router.get("/trip_members/{select}", response_model=list[trip_member_schema.TripMemberResponse], summary="Get trip_member by idUser, idTrip")
def get_trip_member_by(select: str, lookup: str, current_user = Depends(require_role([0]))):
    if select == "idUser":
        trip_member = trip_member_repo.get_trip_member_by_user(lookup)
    elif select == "idTrip":
        trip_member = trip_member_repo.get_trip_member_by_trip(lookup)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    if not trip_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip member not found")
    
    return trip_member

# Get a trip_member by user and trip
@router.get("/trip_members/full/", response_model=trip_member_schema.TripMemberResponse)
def get_trip_member_by_user_trip(idUser: str, idTrip: str, current_user = Depends(require_role([0]))):
    trip_member = trip_member_repo.get_trip_member_by_user_trip(idUser=idUser, idTrip=idTrip)
    if not trip_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip member not found")
    
    return trip_member[0]

# Post a new trip_member
@router.post("/trip_members/", response_model=trip_member_schema.TripMemberResponse)
def create_trip_member(trip_member: trip_member_schema.TripMemberCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, trip_member.iduser)
    
    # Check if the user exists
    if not user_repo.get_user_by_id(trip_member.iduser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Check if the trip exists
    if not trip_repo.get_trip_by_id(trip_member.idtrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    # Check if the trip_member already exists
    if trip_member_repo.get_trip_member_by_user_trip(trip_member.iduser, trip_member.idtrip):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trip member already exists")
    
    return trip_member_repo.create_trip_member(trip_member=trip_member)

# Delete a trip_member
@router.delete("/trip_members", response_model=dict[str, str])
def delete_trip_member(idUser: str, idTrip: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    # Check if the user exists
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Check if the trip exists
    if not trip_repo.get_trip_by_id(idTrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    return trip_member_repo.delete_trip_member(idUser=idUser, idTrip=idTrip)
