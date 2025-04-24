from schemas.trip_member_schema import TripMemberCreate
from repositories import user_repo
from repositories import trip_repo
from fastapi import HTTPException
from supabase_client import supabase

# Get all trip_memnbers
def get_trip_members():
    return supabase.table("tripmembers").select("*").execute().data

# Get a trip_member by
def get_trip_member_by(select: str, lookup: str):
    if select == "idUser":
        return supabase.table("tripmembers").select("*").eq("iduser", lookup).execute().data
    elif select == "idTrip":
        return supabase.table("tripmembers").select("*").eq("idtrip", lookup).execute().data
    else:
        raise HTTPException(400, "Bad Request")
    
# Get a trip_member by user and trip
def get_trip_member_by_user_trip(idUser: str, idTrip: str):
    return supabase.table("tripmembers").select("*").eq("iduser", idUser).eq("idtrip", idTrip).execute().data

# Post a new trip_member
def create_trip_member(trip_member: TripMemberCreate):
    # Check if the user exists
    if not user_repo.get_user_by("idUser", trip_member.iduser):
        raise HTTPException(404, "User not found")
    # Check if the trip exists
    if not trip_repo.get_trip_by_id(trip_member.idtrip):
        raise HTTPException(404, "Trip not found")
    # Check if the trip_member already exists
    if get_trip_member_by_user_trip(trip_member.iduser, trip_member.idtrip):
        raise HTTPException(422, "Trip member already exists")
    
    db_trip_member = {
        "iduser": trip_member.iduser,
        "idtrip": trip_member.idtrip,
    }
    
    response = supabase.table("tripmembers").insert(db_trip_member).execute()
    return response.data[0]

# Delete a trip_member
def delete_trip_member(idUser: str, idTrip: str):
    # Check if the user exists
    if not user_repo.get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    # Check if the trip exists
    if not trip_repo.get_trip_by_id(idTrip):
        raise HTTPException(404, "Trip not found")
    if not get_trip_member_by_user_trip(idUser, idTrip):
        raise HTTPException(404, "Trip member not found")
    
    supabase.table("tripmembers").delete().eq("iduser", idUser).eq("idtrip", idTrip).execute()
    return {"message": "Trip member deleted successfully"}