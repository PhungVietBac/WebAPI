from supabase_client import supabase
from fastapi import HTTPException
from schemas.user_schema import UserCreate, UserUpdate
from repositories import friend_repo
import uuid

# Get all users
def get_users():
    response = supabase.table("users").select("*").execute()
    return response.data

# Get a user by specific field
def get_user_by(select: str, lookup: str):
    if select == "idUser":
        return supabase.table("users").select("*").eq("iduser", lookup).execute().data
    elif select == "username":
        return supabase.table("users").select("*").eq("username", lookup).execute().data
    elif select == "email":
        return supabase.table("users").select("*").eq("email", lookup).execute().data
    elif select == "phoneNumber":
        return supabase.table("users").select("*").eq("phonenumber", lookup).execute().data
    else:
        raise HTTPException(status_code=400, detail="Bad Request")

# Get trips of user
def get_trips_of_user(idUser: str):
    user = get_user_by("idUser", idUser)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = supabase.table("tripmembers").select("idtrip").eq("iduser", idUser).execute().data
    
    trip_ids = [trip["idtrip"] for trip in response]
    
    if not trip_ids:
        raise HTTPException(404, "User hasn't any trip")
    
    return supabase.table("trips").select("*").in_("idtrip", trip_ids).execute().data

# Get bookings of user
def get_bookings_of_user(idUser: str):
    user = get_user_by("idUser", idUser)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = supabase.table("detailbookings").select("idbooking").eq("iduser", idUser).execute()
    
    booking_ids = [booking["idbooking"] for booking in response.data]
    
    if not booking_ids:
        raise HTTPException(status_code=404, detail="User hasn't ever booked")
    
    return supabase.table("bookings").select("*").in_("idbooking", booking_ids).execute().data
    
# Get friend requests of user
def get_friend_requests_of_user(idUser: str):
    user = get_user_by("idUser", idUser)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = supabase.table("friends").select("*").eq("idself", idUser).eq("isaccept", False).execute().data
    friend_ids = [friend["idfriend"] for friend in response]
    
    if not friend_ids:
        raise HTTPException(status_code=404, detail="User hasn't send any friend request")
    
    return supabase.table("users").select("*").in_("iduser", friend_ids).execute().data

# Get friend requests to user
def get_friend_requests_to_user(idUser: str):
    user = get_user_by("idUser", idUser)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = supabase.table("friends").select("*").eq("idfriend", idUser).eq("isaccept", False).execute().data
    friend_ids = [friend["idself"] for friend in response]
    
    if not friend_ids:
        raise HTTPException(404, "User hasn't received any friend request")
    
    return supabase.table("users").select("*").in_("iduser", friend_ids).execute().data

def get_friends_of_user(idUser: str):
    if not get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    
    response = friend_repo.get_friends_by_user(idUser)
    if not response:
        raise HTTPException(404, "This user has no friend")
    
    # Lấy ID bạn bè (loại bỏ chính user đang tìm) và loại trùng
    friend_ids = list(set(
        friend["idself"] if friend["idself"] != idUser else friend["idfriend"]
        for friend in response
    ))

    return supabase.table("users").select("*").in_("iduser", friend_ids).execute().data

# Get reviewed trips of user
def get_reviewed_trips_of_user(idUser: str):
    user = get_user_by("idUser", idUser)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = supabase.table("reviews").select("idtrip").eq("iduser", idUser).execute().data
    trip_ids = [trip["idtrip"] for trip in response]
    
    if not trip_ids:
        raise HTTPException(status_code=404, detail="User hasn't reviewed any trip")
    
    return supabase.table("trips").select("*").in_("idtrip", trip_ids).execute().data

# Post a new user
def create_user(user: UserCreate):
    # Check if the user already exists
    response = supabase.table("users").select("*").or_(
        f"username.eq.{user.username},email.eq.{user.email},phonenumber.eq.{user.phonenumber}"
    ).execute()
    
    if response.data:
        raise HTTPException(status_code=422, detail="User already exists")
    
    # Generate a unique idUser
    idUser = ""
    while not idUser or get_user_by("idUser", idUser):
        idUser = f"US{str(uuid.uuid4())[:4]}"
    
    if user.gender not in [0, 1, 2]:
        raise HTTPException(404, "Bad Request")
    
    db_user = {
        "iduser": idUser,
        "name": user.name,
        "username": user.username,
        "password": user.password,
        "gender": user.gender,
        "email": user.email,
        "phonenumber": user.phonenumber,
        "avatar": user.avatar,
        "theme": 0,
        "language": 0
    }
    
    response = supabase.table("users").insert(db_user).execute()

    return response.data[0]

# Update a user
def update_user(idUser: str, user: UserUpdate):
    db_user = get_user_by("idUser", idUser)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the username, email, or phoneNumber is already taken
    after_users = [
        get_user_by("username", user.username),
        get_user_by("email", user.email),
        get_user_by("phoneNumber", user.phonenumber)
    ]
    
    for after_user in after_users:
        if after_user and after_user[0]["iduser"] != idUser:
            raise HTTPException(status_code=422, detail="User already exists")
    
    # Update user fields
    update_data = {key: value for key, value in user.model_dump(exclude_unset=True).items()}
    
    response = supabase.table("users").update(update_data).eq("iduser", idUser).execute()

    return response.data[0]

# Delete a user
def delete_user(idUser: str):
    db_user = get_user_by("idUser", idUser)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    supabase.table("users").delete().eq("iduser", idUser).execute()
    
    return {"message": "User deleted successfully"}
