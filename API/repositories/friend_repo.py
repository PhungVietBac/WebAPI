from schemas.friend_schema import FriendCreate, FriendUpdate
from fastapi import HTTPException
from repositories import user_repo
from supabase_client import supabase

def get_friends():
    return supabase.table("friends").select("*").execute().data

def get_friends_by_user(user_id: str):
    if not user_repo.get_user_by("idUser", user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    response = supabase.table("friends").select("*").or_(
        f"idself.eq.{user_id},idfriend.eq.{user_id}"
    ).eq("isaccept", True).execute().data

    if not response:
        raise HTTPException(404, "This user has no friend")

    return response

def check_friend(idSelf: str, idFriend: str):
    # Kiểm tra idSelf
    if not user_repo.get_user_by("idUser", idSelf):
        raise HTTPException(status_code=404, detail=f"User {idSelf} not found")

    # Kiểm tra idFriend
    if not user_repo.get_user_by("idUser", idFriend):
        raise HTTPException(status_code=404, detail=f"User {idFriend} not found")

    # Kiểm tra không cho phép kết bạn với chính mình
    if idSelf == idFriend:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")

def create_friend(friend: FriendCreate):
    check_friend(friend.idself, friend.idfriend)
    
    condition = (
        f"and(idself.eq.{friend.idself},idfriend.eq.{friend.idfriend}),"
        f"and(idself.eq.{friend.idfriend},idfriend.eq.{friend.idself})"
    )
    
    if supabase.table("friends").select("*").or_(condition).limit(1).execute().data:
        raise HTTPException(404, "Relationship has existed")

    # Tạo đối tượng Friend từ dữ liệu đầu vào
    db_friend = {
        "idself": friend.idself,
        "idfriend": friend.idfriend,
        "isaccept": False
    }
    
    response = supabase.table("friends").insert(db_friend).execute()
    
    return response.data[0]

def update_friend(friend: FriendUpdate):
    check_friend(friend.idself, friend.idfriend)
    
    query = supabase.table("friends").select("*").or_(
        f"and(idself.eq.{friend.idself},idfriend.eq.{friend.idfriend}),"
        f"and(idself.eq.{friend.idfriend},idfriend.eq.{friend.idself})"
    ).limit(1).execute().data

    if not query:
        raise HTTPException(404, "Relationship not found")

    found = query[0]

    update_data = {key: value for key, value in friend.model_dump(exclude_unset=True).items()}

    updated = supabase.table("friends").update(update_data).eq("idself", found["idself"]).eq("idfriend", found["idfriend"]).execute()

    return updated.data[0]

def delete_friend(id_self: str, id_friend: str):
    check_friend(id_self, id_friend)
    
    query = supabase.table("friends").select("*").or_(
        f"and(idself.eq.{id_self},idfriend.eq.{id_friend}),"
        f"and(idself.eq.{id_friend},idfriend.eq.{id_self})"
    ).limit(1).execute().data

    if not query:
        raise HTTPException(404, "Relationship not found")

    found = query[0]

    supabase.table("friends").delete().eq("idself", found["idself"]).eq("idfriend", found["idfriend"]).execute()

    return {"message": "Relationship deleted successfully"}