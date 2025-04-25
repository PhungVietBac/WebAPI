from schemas.notification_schema import NotificationUpdate, NotificationCreate
import uuid
from supabase_client import supabase

# Get all notifications
def get_notifications(skip: int, limit: int):
    return supabase.table("notifications").select("*").range(skip, skip + limit - 1).execute().data

# Get notification by id
def get_notification_by_id(idNotf: str):
    return supabase.table("notifications").select("*").eq("idnotf", idNotf).limit(1).execute().data
    
# Get notifications by User
def get_notification_by_user(idUser: str, skip: int, limit: int):
    return supabase.table("notifications").select("*").eq("iduser", idUser).range(skip, skip + limit - 1).execute().data
    
def get_unread_notifications(user_id: str, skip: int, limit: int):    
    return supabase.table("notifications").select("*").eq("iduser", user_id).eq("isread", False).range(skip, skip + limit - 1).execute().data
    
# Post a new notification
def create_notification(notification: NotificationCreate):
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
    update_data = {key: value for key, value in notification.model_dump(exclude_unset=True).items()}
    
    response = supabase.table("notifications").update(update_data).eq("idnotf", idNotify).execute()
    
    return response.data[0]

def is_user_has_notification(idUser: str):
    response = supabase.table("notifications").select("*").eq("iduser", idUser).limit(1).execute()
    return bool(response.data)

# Mark all notifications as read by user
def mark_all_notifications_as_read(idUser: str):
    response = supabase.table("notifications").update({"isread": True}).eq("iduser", idUser).execute()
    
    return response.data

# Delete a notification
def delete_notification(idNotify: str):
    supabase.table("notifications").delete().eq("idnotf", idNotify).execute()
    return {"message": "Notification deleted successfully"}

# Delete all notifications by user
def delete_notifications_by_user(idUser: str):
    supabase.table("notifications").delete().eq("iduser", idUser).execute()
    return {"message": "All notifications deleted successfully"}