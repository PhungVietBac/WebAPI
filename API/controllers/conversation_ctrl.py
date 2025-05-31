from fastapi import APIRouter, HTTPException, Depends, status
from schemas import conversation_schema, message_schema
from controllers.auth_ctrl import require_role, assert_owner_or_admin
from repositories import conversation_repo, user_repo
import math

router = APIRouter()

@router.get("/{id}", response_model=conversation_schema.ConversationResponse)
def get_conversation_by_id(id: str, current_user = Depends(require_role([0, 1]))):
    conversation = conversation_repo.get_conversations_by_id(id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    assert_owner_or_admin(current_user, conversation[0]["user_id"])
    return conversation[0]

@router.post("/", response_model=conversation_schema.ConversationResponse)
def create_conversation(conversation: conversation_schema.ConversationCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, conversation.user_id)
    if not user_repo.get_user_by_id(conversation.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return conversation_repo.create_conversation(conversation)

@router.put("/{id}", response_model=conversation_schema.ConversationResponse)
def update_conversation(id: str, conversation: conversation_schema.ConversationUpdate, current_user = Depends(require_role([0, 1]))):
    cvst = conversation_repo.get_conversations_by_id(id)
    if not cvst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    user_id = cvst[0]["user_id"]
    assert_owner_or_admin(current_user, user_id)
    
    return conversation_repo.update_conversation(id, conversation)


@router.delete("/{id}", response_model=dict[str, str])
def delete_conversation(id: str, current_user = Depends(require_role([0, 1]))):
    cvst = conversation_repo.get_conversations_by_id(id)
    if not cvst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    user_id = cvst[0]["user_id"]
    assert_owner_or_admin(current_user, user_id)
    
    return conversation_repo.delete_conversation(id)    

@router.get("/{id}/messages", response_model=message_schema.CombineResponse)
def get_messages_by_conversation(id: str, page: int = 1, limit: int = 50, current_user = Depends(require_role([0, 1]))):
    if not conversation_repo.get_conversations_by_id(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    user = conversation_repo.get_user_by_conversation(id)
    assert_owner_or_admin(current_user, user)
    
    messages, total = conversation_repo.get_messages_by_conversation(id, page, limit)
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No message found")
    
    pagination = conversation_schema.Pagination(
        page = page, 
        limit = limit,
        total = total,
        totalPages = math.ceil(total / limit),
        hasNext = page*limit < total, 
        hasPrev = page > 1
    )
    
    res = message_schema.CombineResponse(
        messages = messages, 
        pagination = pagination
    ) 
    return res
    
    
    