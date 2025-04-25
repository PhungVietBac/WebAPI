from supabase_client import supabase
from schemas.user_schema import UserCreate, UserUpdate
import uuid

# Get all users
def get_users():
    response = supabase.table("users").select("*").execute()
    return response.data

# Get an user by specific field    
def get_user_by_id(idUser: str):
    return supabase.table("users").select("*").eq("iduser", idUser).execute().data

def get_user_by_username(username: str):
    return supabase.table("users").select("*").eq("username", username).execute().data

def get_user_by_email(email: str):
    return supabase.table("users").select("*").eq("email", email).execute().data

def get_user_by_phone(phone: str):
    return supabase.table("users").select("*").eq("phonenumber", phone).execute().data

# Get trips of user
def get_trip_ids_of_user(idUser: str):
    response = supabase.table("tripmembers").select("idtrip").eq("iduser", idUser).execute().data
    
    return [trip["idtrip"] for trip in response]
    
# Get bookings of user
def get_booking_ids_of_user(idUser: str):
    response = supabase.table("detailbookings").select("idbooking").eq("iduser", idUser).execute()
    
    return [booking["idbooking"] for booking in response.data]
    
# Get friend requests of user
def get_friend_request_ids_of_user(idUser: str):
    response = supabase.table("friends").select("*").eq("idself", idUser).eq("isaccept", False).execute().data
    return [friend["idfriend"] for friend in response]

# Get friend requests to user
def get_friend_request_ids_to_user(idUser: str):
    response = supabase.table("friends").select("*").eq("idfriend", idUser).eq("isaccept", False).execute().data
    return [friend["idself"] for friend in response]

def get_friends_of_user(idUser: str, friendList):
    # Lấy ID bạn bè (loại bỏ chính user đang tìm) và loại trùng
    friend_ids = list(set(
        friend["idself"] if friend["idself"] != idUser else friend["idfriend"]
        for friend in friendList
    ))

    return supabase.table("users").select("*").in_("iduser", friend_ids).execute().data

# Get reviewed trips of user
def get_reviewed_trip_ids_of_user(idUser: str):
    response = supabase.table("reviews").select("idtrip").eq("iduser", idUser).execute().data
    return [trip["idtrip"] for trip in response]

def get_ai_recommendations_of_user(idUser: str):
    response = supabase.table("airecommendations").select("*").eq("iduser", idUser).execute().data

# Check if the user already exists
def is_user_exist(user: UserCreate):
    response = supabase.table("users").select("*").or_(
        f"username.eq.{user.username},email.eq.{user.email},phonenumber.eq.{user.phonenumber}"
    ).execute()
    return bool(response.data)

def is_valid_user(user: UserCreate):
    if user.gender not in [0, 1, 2]:
        return False
    return True

# Post a new user
def create_user(user: UserCreate):    
    # Generate a unique idUser
    idUser = ""
    while not idUser or get_user_by_id(idUser):
        idUser = f"US{str(uuid.uuid4())[:4]}"
    
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
        "language": 0,
        "description": user.description,
        "role": 1
    }
    
    response = supabase.table("users").insert(db_user).execute()

    return response.data[0]

def check_after_update_user(user: UserCreate, idUser: str):
    # Check if the username, email, or phoneNumber is already taken
    after_users = [
        get_user_by_username(user.username),
        get_user_by_email(user.email),
        get_user_by_phone(user.phonenumber)
    ]
    
    for after_user in after_users:
        if after_user and after_user[0]["iduser"] != idUser:
            return False
        
    return True

# Update a user
def update_user(idUser: str, user: UserUpdate):
    # Update user fields
    update_data = {key: value for key, value in user.model_dump(exclude_unset=True).items()}
    
    response = supabase.table("users").update(update_data).eq("iduser", idUser).execute()

    return response.data[0]

# Delete a user
def delete_user(idUser: str):
    supabase.table("users").delete().eq("iduser", idUser).execute()
    
    return {"message": "User deleted successfully"}
