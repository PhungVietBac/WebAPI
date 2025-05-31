from fastapi import APIRouter, HTTPException, Depends, status
from controllers.auth_ctrl import require_role, assert_owner_or_admin
from schemas import message_schema
from repositories import message_repo, conversation_repo

router = APIRouter()

@router.get("/{id}", response_model=message_schema.MessageResponse)
def get_message_by_id(id: str, current_user = Depends(require_role([0, 1]))):
    message = message_repo.get_message_by_id(id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    user = message_repo.get_user_by_message(id)
    assert_owner_or_admin(current_user, user)
    
    return message[0]

@router.post("/", response_model=message_schema.MessageResponse)
def create_message(message: message_schema.MessageCreate, current_user = Depends(require_role([0, 1]))):
    conversation = conversation_repo.get_conversations_by_id(message.conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    user = conversation_repo.get_user_by_conversation(conversation[0]["id"])
    assert_owner_or_admin(current_user, user)
    
    return message_repo.create_message(message)