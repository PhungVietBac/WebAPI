from fastapi import APIRouter, HTTPException, Depends, status
from schemas import ai_recommendation_schema
from repositories import ai_recommendation_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/ai_recs", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_recs(current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return ai_recommendation_repo.get_aiRec(skip, limit)

@router.get("/ai_recs/id/{idAIRec}", response_model=ai_recommendation_schema.AIRecResponse)
def get_ai_rec_by_id(idAIRec: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    ai_rec = ai_recommendation_repo.get_aiRec_by_id(idAIRec)
    if not ai_rec:
        raise HTTPException(404, "AI recommendation not found")
    
    return ai_rec[0]

@router.get("/ai_recs/{idUser}", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_rec_by_user(idUser: str, current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return ai_recommendation_repo.get_aiRec_by_user(idUser, skip, limit)

@router.post("/ai_recs/", response_model=ai_recommendation_schema.AIRecResponse)
def create_ai_rec(ai_rec: ai_recommendation_schema.AIRecCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return ai_recommendation_repo.create_aiRec(ai_rec)

@router.delete("/ai_recs/{idAIRec}", response_model=dict[str, str])
def delete_ai_rec(idAIRec: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return ai_recommendation_repo.delete_aiRec(idAIRec)
