from schemas.ai_recommendation_schema import AIRecCreate
import uuid
from supabase_client import supabase

# Get all AI recommendations
def get_aiRec(skip: int, limit: int):
    return supabase.table("airecommendations").select("*").range(skip, skip + limit - 1).execute().data

# Get AI recommendation by
def get_aiRec_by_id(idAIRec: str):
    return supabase.table("airecommendations").select("*").eq("idairec", idAIRec).limit(1).execute().data
    
def get_aiRec_by_user(idUser: str, skip: int, limit: int):   
    return supabase.table("airecommendations").select("*").eq("iduser", idUser).range(skip, skip + limit - 1).execute().data

# Post new AI recommendation
def create_aiRec(aiRecommendation: AIRecCreate):
    idAIRec = ""
    while not idAIRec or get_aiRec_by_id(idAIRec):
        idAIRec = f"AI{str(uuid.uuid4())[:4]}"

    db_AIRecommendation = {
        "idairec": idAIRec,
        "iduser": aiRecommendation.iduser,
        "input": aiRecommendation.input,
        "output": ""
    }
    
    return supabase.table("airecommendations").insert(db_AIRecommendation).execute().data[0]
    
# Delete AI recommendation
def delete_aiRec(idAIRec: str):   
    supabase.table("airecommendations").delete().eq("idairec", idAIRec).execute()
    return {"message": "AI recommendation deleted successfully"}