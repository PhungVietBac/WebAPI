from fastapi import APIRouter, Depends, HTTPException, status
from schemas import user_schema, trip_schema, booking_schema, place_schema
from repositories import user_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

# Get all users
@router.get("/users/", response_model=list[user_schema.UserResponse])
def get_users(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_users()

# Get a user by
@router.get("/users/{select}", response_model=user_schema.UserResponse)
def get_user_by(select: str, lookup: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    user = user_repo.get_user_by(select=select, lookup=lookup)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user[0]

@router.get("/users/{idUser}/trips", response_model=list[trip_schema.TripResponse])
def get_trips_of_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_trips_of_user(idUser)

@router.get("/users/{idUser}/friends", response_model=list[user_schema.UserResponse])
def get_friends_of_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_friends_of_user(idUser)

@router.get("/users/{idUser}/bookings", response_model=list[booking_schema.BookingResponse])
def get_bookings_of_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_bookings_of_user(idUser)

@router.get("/users/{idUser}/friend_requests_of", response_model=list[user_schema.UserResponse])
def get_friend_requests_of_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_friend_requests_of_user(idUser)

@router.get("/users/{idUser}/friend_requests_to", response_model=list[user_schema.UserResponse])
def get_friend_requests_to_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_friend_requests_to_user(idUser)

@router.get("/users/{idUser}/reviewed_trips", response_model=list[trip_schema.TripResponse])
def get_reviewed_trips_of_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.get_reviewed_trips_of_user(idUser)

# Post a new user
@router.post("/users/", response_model=user_schema.UserResponse)
def create_user(user: user_schema.UserCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.create_user(user=user)

# Update a user
@router.put("/users/{idUser}", response_model=user_schema.UserResponse)
def update_user(idUser: str, user: user_schema.UserUpdate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.update_user(idUser=idUser, user=user)

# Delete a user
@router.delete("/users/{idUser}", response_model=dict[str, str])
def delete_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return user_repo.delete_user(idUser=idUser)