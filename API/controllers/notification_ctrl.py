from fastapi import APIRouter, Depends, HTTPException, status
from schemas import notification_schema
from repositories import notification_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

# Get all notifcations
@router.get("/notifications/", response_model=list[notification_schema.NotificationResponse])
def get_notifications(current_user = Depends(get_current_user), skip: int =0, limit: int = 100):
    check_authorization(current_user)
    
    return notification_repo.get_notifications(skip, limit)

# Get notification by id
@router.get("/notifications", response_model=notification_schema.NotificationResponse)
def get_notification_by_id(idNotf: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    notf = notification_repo.get_notification_by_id(idNotf)
    if not notf:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notf[0]

# Get notification by user
@router.get("/notifications/{idUser}", response_model=list[notification_schema.NotificationResponse])
def get_notification_by_user(idUser: str, current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return notification_repo.get_notification_by_user(idUser, skip, limit)

@router.get("notifications/unread/{user_id}", response_model=list[notification_schema.NotificationResponse])
def get_unread_notifications(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    check_authorization(current_user)
    
    """Get all unread notifications for a specific user"""
    return notification_repo.get_unread_notifications(user_id, skip, limit)

# Post a new notification
@router.post("/notifications/", response_model=notification_schema.NotificationResponse)
def create_notification(notification: notification_schema.NotificationCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return notification_repo.create_notification(notification)

# Update a notification
@router.put("/notifications/{idNotify}", response_model=notification_schema.NotificationResponse)
def update_notification(idNotify: str, notification: notification_schema.NotificationUpdate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return notification_repo.update_notification(idNotify, notification)

# Mark all notifications as read by user
@router.put("/notifications/mark-all/{idUser}", response_model=list[notification_schema.NotificationResponse])
def mark_all_notifications_as_read(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return notification_repo.mark_all_notifications_as_read(idUser)

# Delete a notification
@router.delete("/notifications/{idNotify}", response_model=dict[str, str])
def delete_notification(idNotify: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return notification_repo.delete_notification(idNotify)

# Delete all notifications by user
@router.delete("/notifications/delete-all/{idUser}", response_model=dict[str, str])
def delete_all_notifications_by_user(idUser: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return notification_repo.delete_notifications_by_user(idUser)
