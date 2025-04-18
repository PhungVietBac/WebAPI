from schemas.notification_schema import NotificationUpdate, NotificationCreate
from repositories import user_repo
import uuid
from fastapi import HTTPException
from supabase_client import supabase

# Get all notifications
def get_notifications(skip: int, limit: int):
    return supabase.table("notifications").select("*").range(skip, skip + limit - 1).execute().data

# Get notification by id
def get_notification_by_id(idNotf: str):
    return supabase.table("notifications").select("*").eq("idnotf", idNotf).execute().data
    
# Get notifications by User
def get_notification_by_user(idUser: str, skip: int, limit: int):
    if not user_repo.get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    
    response = supabase.table("notifications").select("*").eq("iduser", idUser).range(skip, skip + limit - 1).execute().data
    
    if not response:
        raise HTTPException(404, "User has no any notifications")
    
    return response

def get_unread_notifications(user_id: str, skip: int, limit: int):
    if not user_repo.get_user_by("idUser", user_id):
        raise HTTPException(404, "User not found")
    
    response = supabase.table("notifications").select("*").eq("iduser", user_id).eq("isread", False).range(skip, skip + limit - 1).execute().data
    
    if not response:
        raise HTTPException(404, "User has no any unread notifications")
    
    return response
    
# Post a new notification
def create_notification(notification: NotificationCreate):
    user = user_repo.get_user_by("idUser", notification.iduser)
    if not user:
        raise HTTPException(404, "User not found")
    
    idNotify = ""
    while not idNotify or get_notification_by_id(idNotify):
        idNotify = f"NTF{str(uuid.uuid4())[:3]}"
    
    db_notification = {
        "idnotf": idNotify,
        "iduser": notification.iduser,
        "content": notification.content,
        "isread": False
    }

    response = supabase.table("notifications").insert(db_notification).execute().data
    
    return response[0]

# Update a notification
def update_notification(idNotify: str, notification: NotificationUpdate):
    db_notification = get_notification_by_id(idNotify)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_data = {key: value for key, value in notification.model_dump(exclude_unset=True).items()}
    
    response = supabase.table("notifications").update(update_data).eq("idnotf", idNotify).execute()
    
    return response.data[0]

# Mark all notifications as read by user
def mark_all_notifications_as_read(idUser: str):
    if not user_repo.get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    
    if not supabase.table("notifications").select("*").eq("iduser", idUser).execute().data:
        raise HTTPException(404, "User has no any notifications")
    
    response = supabase.table("notifications").update({"isread": True}).eq("iduser", idUser).execute()
    
    return response.data

# Delete a notification
def delete_notification(idNotify: str):
    db_notification = get_notification_by_id(idNotify)

    if not db_notification:
        raise HTTPException(404, "Notification not found")
    
    supabase.table("notifications").delete().eq("idnotf", idNotify).execute()
    return {"message": "Notification deleted successfully"}

# Delete all notifications by user
def delete_notifications_by_user(idUser: str):
    if not user_repo.get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    
    if not supabase.table("notifications").select("*").eq("iduser", idUser).execute().data:
        raise HTTPException(404, "User has no any notifications")
    
    supabase.table("notifications").delete().eq("iduser", idUser).execute()
    return {"message": "All notifications deleted successfully"}