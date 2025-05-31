from schemas.message_schema import MessageCreate, MessageUpdate
import uuid
from supabase_client import supabase
from datetime import datetime

def get_message_by_id(id: str):
    return supabase.table("messages").select("*").eq("id", id).execute().data

def get_conversation_by_message(id: str):
    return supabase.table("messages").select("conversation_id").eq("id", id).execute().data[0]["conversation_id"]

def get_user_by_message(id: str):
    idConversation = get_conversation_by_message(id)
    return supabase.table("conversations").select("user_id").eq("id", idConversation).execute().data[0]["user_id"]

def create_message(message: MessageCreate):
    idMessage = ""
    while not idMessage or get_message_by_id(idMessage):
        idMessage = f"M{str(uuid.uuid4())[:5]}"
        
    created_at_str = message.created_at.isoformat()
    
    db_message = {
        "id": idMessage,
        "conversation_id": message.conversation_id,
        "content": message.content,
        "role": message.role,
        "created_at": created_at_str,
        "metadata": message.metadata,
        "token_count": message.token_count
    }
    
    response = supabase.table("messages").insert(db_message).execute()
    supabase.table("conversations").update({"updated_at": datetime.now().isoformat()}).eq("id", message.conversation_id).execute()
    return response.data[0]
    
    
    
    