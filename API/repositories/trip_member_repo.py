from schemas.trip_member_schema import TripMemberCreate
from supabase_client import supabase

# Get all trip_memnbers
def get_trip_members():
    return supabase.table("tripmembers").select("*").execute().data

# Get a trip_member by
def get_trip_member_by_user(idUser: str):
    return supabase.table("tripmembers").select("*").eq("iduser", idUser).execute().data

def get_trip_member_by_trip(idTrip: str):
    return supabase.table("tripmembers").select("*").eq("idtrip", idTrip).execute().data
    
# Get a trip_member by user and trip
def get_trip_member_by_user_trip(idUser: str, idTrip: str):
    return supabase.table("tripmembers").select("*").eq("iduser", idUser).eq("idtrip", idTrip).execute().data

# Post a new trip_member
def create_trip_member(trip_member: TripMemberCreate):
    db_trip_member = {
        "iduser": trip_member.iduser,
        "idtrip": trip_member.idtrip,
    }
    
    response = supabase.table("tripmembers").insert(db_trip_member).execute()
    return response.data[0]

# Delete a trip_member
def delete_trip_member(idUser: str, idTrip: str):
    supabase.table("tripmembers").delete().eq("iduser", idUser).eq("idtrip", idTrip).execute()
    return {"message": "Trip member deleted successfully"}