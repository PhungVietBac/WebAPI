from schemas.friend_schema import FriendCreate, FriendUpdate
from supabase_client import supabase

def get_friends():
    return supabase.table("friends").select("*").execute().data

def get_friends_by_user(user_id: str):
    return supabase.table("friends").select("*").or_(
        f"idself.eq.{user_id},idfriend.eq.{user_id}"
    ).eq("isaccept", True).execute().data
    
def is_relation_exists(idSelf: str, idFriend: str):
    condition = (
        f"and(idself.eq.{idSelf},idfriend.eq.{idFriend}),"
        f"and(idself.eq.{idFriend},idfriend.eq.{idSelf})"
    )
    
    return supabase.table("friends").select("*").or_(condition).limit(1).execute().data

def create_friend(friend: FriendCreate):
    # Tạo đối tượng Friend từ dữ liệu đầu vào
    db_friend = {
        "idself": friend.idself,
        "idfriend": friend.idfriend,
        "isaccept": False
    }
    
    response = supabase.table("friends").insert(db_friend).execute()
    
    return response.data[0]

def update_friend(friend: FriendUpdate, found):
    update_data = {key: value for key, value in friend.model_dump(exclude_unset=True).items()}

    updated = supabase.table("friends").update(update_data).eq("idself", found["idself"]).eq("idfriend", found["idfriend"]).execute()

    return updated.data[0]

def delete_friend(id_self: str, id_friend: str, found):
    supabase.table("friends").delete().eq("idself", found["idself"]).eq("idfriend", found["idfriend"]).execute()

    return {"message": "Relationship deleted successfully"}