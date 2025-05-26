from fastapi import APIRouter, Depends, HTTPException, status
from schemas import notification_schema
from repositories import notification_repo, user_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin

router = APIRouter()

# Get all notifcations
@router.get("/notifications/", response_model=list[notification_schema.NotificationResponse])
def get_notifications(current_user = Depends(require_role([0])), skip: int =0, limit: int = 100):
    
    return notification_repo.get_notifications(skip, limit)

# Get notification by id
@router.get("/notifications", response_model=notification_schema.NotificationResponse)
def get_notification_by_id(idNotf: str, current_user = Depends(require_role([0, 1]))):
    notf = notification_repo.get_notification_by_id(idNotf)
    if not notf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    assert_owner_or_admin(current_user, notf[0]["iduser"])
    
    return notf[0]

# Get notification by user
@router.get("/notifications/{idUser}", response_model=list[notification_schema.NotificationResponse])
def get_notification_by_user(idUser: str, current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    assert_owner_or_admin(current_user, idUser)

    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    response = notification_repo.get_notification_by_user(idUser, skip, limit)

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no any notifications")
    
    return response

@router.get("notifications/unread/{user_id}", response_model=list[notification_schema.NotificationResponse])
def get_unread_notifications(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(require_role([0, 1]))
):
    assert_owner_or_admin(current_user, user_id)

    if not user_repo.get_user_by_id(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    """Get all unread notifications for a specific user"""
    response = notification_repo.get_unread_notifications(user_id, skip, limit)
    
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no any unread notifications")
    
    return response

# Post a new notification
@router.post("/notifications/", response_model=notification_schema.NotificationResponse)
def create_notification(notification: notification_schema.NotificationCreate, current_user = Depends(require_role([0]))):
    if not user_repo.get_user_by_id(notification.iduser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return notification_repo.create_notification(notification)

# Update a notification
@router.put("/notifications/{idNotify}", response_model=notification_schema.NotificationResponse)
def update_notification(idNotify: str, notification: notification_schema.NotificationUpdate, current_user = Depends(require_role([0, 1]))):
    db_notification = get_notification_by_id(idNotify)
    if not db_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    assert_owner_or_admin(current_user, db_notification[0]["iduser"])
    
    return notification_repo.update_notification(idNotify, notification)

# Mark all notifications as read by user
@router.put("/notifications/mark-all/{idUser}", response_model=list[notification_schema.NotificationResponse])
def mark_all_notifications_as_read(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)

    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not notification_repo.is_user_has_notification(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No any notification found")
    
    return notification_repo.mark_all_notifications_as_read(idUser)

# Delete a notification
@router.delete("/notifications/{idNotify}", response_model=dict[str, str])
def delete_notification(idNotify: str, current_user = Depends(require_role([0, 1]))):
    db_notification = get_notification_by_id(idNotify)
    if not db_notification:
        raise HTTPException(404, "Notification not found")
    
    assert_owner_or_admin(current_user, db_notification[0]["iduser"])
    
    return notification_repo.delete_notification(idNotify)

# Delete all notifications by user
@router.delete("/notifications/delete-all/{idUser}", response_model=dict[str, str])
def delete_all_notifications_by_user(idUser: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, idUser)

    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not notification_repo.is_user_has_notification(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No any notification found")
    
    return notification_repo.delete_notifications_by_user(idUser)
