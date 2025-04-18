from schemas.ai_recommendation_schema import AIRecCreate
from repositories import user_repo
from fastapi import HTTPException
import uuid
from supabase_client import supabase

# Get all AI recommendations
def get_aiRec(skip: int, limit: int):
    return supabase.table("airecommendations").select("*").range(skip, skip + limit - 1).execute().data

# Get AI recommendation by
def get_aiRec_by_id(idAIRec: str):
    return supabase.table("airecommendations").select("*").eq("idairec", idAIRec).execute().data
    
def get_aiRec_by_user(idUser: str, skip: int, limit: int):
    if not user_repo.get_user_by("idUser", idUser):
        raise HTTPException(404, "User not found")
    
    response = supabase.table("airecommendations").select("*").eq("iduser", idUser).range(skip, skip + limit - 1).execute().data
    
    if not response:
        raise HTTPException(404, "AI recommendation not found")
    return response

# Post new AI recommendation
def create_aiRec(aiRecommendation: AIRecCreate):
    if not user_repo.get_user_by("idUser", aiRecommendation.iduser):
        raise HTTPException(404, "User not found")
    
    idAIRec = ""
    while not idAIRec or get_aiRec_by_id(idAIRec):
        idAIRec = f"AI{str(uuid.uuid4())[:4]}"

    db_AIRecommendation = {
        "idairec": idAIRec,
        "iduser": aiRecommendation.iduser,
        "input": aiRecommendation.input,
        "output": ""
    }
    
    response = supabase.table("airecommendations").insert(db_AIRecommendation).execute()

    return response.data[0]

# Delete AI recommendation
def delete_aiRec(idAIRec: str):
    if not get_aiRec_by_id(idAIRec):
        raise HTTPException(404, "AI recommendation not found")
    
    supabase.table("airecommendations").delete().eq("idairec", idAIRec).execute()
    return {"message": "AI recommendation deleted successfully"}