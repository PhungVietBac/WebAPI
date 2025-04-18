from fastapi import APIRouter, Depends, HTTPException, status
import schemas.friend_schema as friend_schema
from repositories import friend_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/friends/", response_model=list[friend_schema.FriendResponse])
def get_all_friends(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return friend_repo.get_friends()

@router.get("/friends/{user_id}", response_model=list[friend_schema.FriendResponse])
def get_friends(user_id: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)

    return friend_repo.get_friends_by_user(user_id)

@router.post("/friends/", response_model=friend_schema.FriendResponse)
def create_new_friend(friend: friend_schema.FriendCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    # Tạo quan hệ bạn bè
    return friend_repo.create_friend(friend)

@router.put("/friends/", response_model=friend_schema.FriendResponse)
def update_friend(friend: friend_schema.FriendUpdate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    # Tạo quan hệ bạn bè
    return friend_repo.update_friend(friend)

@router.delete("/friends", response_model=dict[str, str])
def delete_friend(id_self: str, id_friend: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)

    # Xóa quan hệ bạn bè
    return friend_repo.delete_friend(id_self, id_friend)