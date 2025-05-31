from fastapi import APIRouter, Depends, HTTPException, status
import schemas.friend_schema as friend_schema
from repositories import friend_repo, user_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin

router = APIRouter()

@router.get("/", response_model=list[friend_schema.FriendResponse])
def get_all_friends(current_user = Depends(require_role([0]))):
    return friend_repo.get_friends()

@router.get("/{user_id}", response_model=list[friend_schema.FriendResponse])
def get_friends(user_id: str, current_user = Depends(require_role([0, 1]))):
    if not user_repo.get_user_by_id(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") 
    
    response = friend_repo.get_friends_by_user(user_id)
    
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user has no friend")
    
    return response

@router.post("/", response_model=friend_schema.FriendResponse)
def create_new_friend(friend: friend_schema.FriendCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, friend.idself)
    
    # Kiểm tra idSelf
    if not user_repo.get_user_by_id(friend.idself):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {friend.idself} not found")

    # Kiểm tra idFriend
    if not user_repo.get_user_by_id(friend.idfriend):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {friend.idfriend} not found")

    # Kiểm tra không cho phép kết bạn với chính mình
    if friend.idself == friend.idfriend:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add yourself as a friend")
    
    if friend_repo.is_relation_exists(friend.idself, friend.idfriend):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Relationship has existed")
    
    # Tạo quan hệ bạn bè
    return friend_repo.create_friend(friend)

@router.put("/", response_model=friend_schema.FriendResponse)
def update_friend(friend: friend_schema.FriendUpdate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, friend.idself)
    
    # Kiểm tra idSelf
    if not user_repo.get_user_by_id(friend.idself):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {friend.idself} not found")

    # Kiểm tra idFriend
    if not user_repo.get_user_by_id(friend.idfriend):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {friend.idfriend} not found")

    # Kiểm tra không cho phép kết bạn với chính mình
    if friend.idself == friend.idfriend:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add yourself as a friend")
    
    relation = friend_repo.is_relation_exists(friend.idself, friend.idfriend)
    if not relation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    
    # Tạo quan hệ bạn bè
    return friend_repo.update_friend(friend, relation[0])

@router.delete("/", response_model=dict[str, str])
def delete_friend(id_self: str, id_friend: str, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, id_self)
    
    # Kiểm tra idSelf
    if not user_repo.get_user_by_id(id_self):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id_self} not found")

    # Kiểm tra idFriend
    if not user_repo.get_user_by_id(id_friend):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id_friend} not found")
    
    relation = friend_repo.is_relation_exists(id_self, id_friend)
    if not relation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    
    # Xóa quan hệ bạn bè
    return friend_repo.delete_friend(id_self, id_friend, relation[0])