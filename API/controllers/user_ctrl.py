from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from schemas import user_schema, trip_schema, booking_schema, ai_recommendation_schema
from repositories import user_repo, trip_repo, friend_repo, booking_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin
from services.storage_service import upload_avatar, delete_old_avatar

router = APIRouter()

# Get all users
@router.get("/users/", response_model=list[user_schema.UserResponse])
def get_users(current_user = Depends(require_role([0, 1]))):
    return user_repo.get_users()

# Get a user by
@router.get("/users/{select}", response_model=user_schema.UserResponse)
def get_user_by(select: str, lookup: str, current_user = Depends(require_role([0, 1]))):
    if select == "idUser":
        user = user_repo.get_user_by_id(lookup)
    elif select == "username":
        user = user_repo.get_user_by_username(lookup)
    elif select == "email":
        user = user_repo.get_user_by_email(lookup)
    elif select == "phoneNumber":
        user = user_repo.get_user_by_phone(lookup)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user[0]

@router.get("/users/{idUser}/trips", response_model=list[trip_schema.TripResponse])
def get_trips_of_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    trip_ids = user_repo.get_trips_of_user(idUser)
    
    if not trip_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't any trip")
    
    return [trip_repo.get_trip_by_id(trip_id) for trip_id in trip_ids]

@router.get("/users/{idUser}/friends", response_model=list[user_schema.UserResponse])
def get_friends_of_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    response = friend_repo.get_friends_by_user(idUser)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user has no friend")
    
    return user_repo.get_friends_of_user(idUser, response)

@router.get("/users/{idUser}/bookings", response_model=list[booking_schema.BookingResponse])
def get_bookings_of_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    booking_ids = user_repo.get_booking_ids_of_user(idUser)
    
    if not booking_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't ever booked")
    
    return [booking_repo.get_booking_by_id(booking_id) for booking_id in booking_ids]

@router.get("/users/{idUser}/friend_requests_of", response_model=list[user_schema.UserResponse])
def get_friend_requests_of_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    friend_ids = user_repo.get_friend_request_ids_of_user(idUser)
    
    if not friend_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't send any friend request")
    
    return [user_repo.get_user_by_id(friend_id) for friend_id in friend_ids]

@router.get("/users/{idUser}/friend_requests_to", response_model=list[user_schema.UserResponse])
def get_friend_requests_to_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    friend_ids = user_repo.get_friend_request_ids_to_user(idUser)
    
    if not friend_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't received any friend request")
    
    return [user_repo.get_user_by_id(friend_id) for friend_id in friend_ids]

@router.get("/users/{idUser}/reviewed_trips", response_model=list[trip_schema.TripResponse])
def get_reviewed_trips_of_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    trip_ids = user_repo.get_reviewed_trip_ids_of_user(idUser)
    
    if not trip_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't reviewed any trip")
    
    return [trip_repo.get_trip_by_id(trip_id) for trip_id in trip_ids]

@router.get("/users/{idUser}/ai_recs", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_recs_of_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    response = user_repo.get_ai_recommendations_of_user(idUser)
    
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't any AI recommendation")
    
    return response

# Post a new user
@router.post("/users/", response_model=user_schema.UserResponse)
def create_user(user: user_schema.UserCreate, current_user = Depends(require_role([0, 1]))):
    if user_repo.is_user_exist(user):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    if not user_repo.is_valid_user(user):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid gender")
    
    return user_repo.create_user(user=user)

@router.post("/users/ava")

# Update a user
@router.put("/users/{idUser}", response_model=user_schema.UserResponse)
def update_user(idUser: str, user: user_schema.UserUpdate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user_repo.is_valid_user(user):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid gender")
    
    if not user_repo.check_after_update_user(user, idUser):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        
    return user_repo.update_user(idUser=idUser, user=user)

@router.patch("/users/{idUser}/avatar")
async def change_avatar(idUser: str, file: UploadFile = File(...), current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    user = user_repo.get_user_by_id(idUser)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        delete_old_avatar(user[0]["avatar"])
        publicUrl = await upload_avatar(file)
        user = user_repo.update_user_avatar(idUser, publicUrl)
        return {"message": "Avatar updated", "avatar_url": publicUrl, "user": user}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Delete a user
@router.delete("/users/{idUser}", response_model=dict[str, str])
def delete_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user_repo.delete_user(idUser=idUser)