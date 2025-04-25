from fastapi import APIRouter, HTTPException, Depends, status
from schemas import ai_recommendation_schema
from repositories import ai_recommendation_repo, user_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin

router = APIRouter()

@router.get("/ai_recs", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_recs(current_user = Depends(require_role([0])), skip: int = 0, limit: int = 100):
    
    return ai_recommendation_repo.get_aiRec(skip, limit)

@router.get("/ai_recs/id/{idAIRec}", response_model=ai_recommendation_schema.AIRecResponse)
def get_ai_rec_by_id(idAIRec: str, current_user = Depends(require_role([0, 1]))):
    
    ai_rec = ai_recommendation_repo.get_aiRec_by_id(idAIRec)
    if not ai_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI recommendation not found")
    
    assert_owner_or_admin(current_user, ai_rec[0]["iduser"])
    
    return ai_rec[0]

@router.get("/ai_recs/{idUser}", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_rec_by_user(idUser: str, current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100): 
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    response = ai_recommendation_repo.get_aiRec_by_user(idUser, skip, limit)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No AI recommendations found")
    
    return response

@router.post("/ai_recs/", response_model=ai_recommendation_schema.AIRecResponse)
def create_ai_rec(ai_rec: ai_recommendation_schema.AIRecCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, ai_rec.iduser)
    
    if not user_repo.get_user_by_id(ai_rec.iduser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return ai_recommendation_repo.create_aiRec(ai_rec)

@router.delete("/ai_recs/{idAIRec}", response_model=dict[str, str])
def delete_ai_rec(idAIRec: str, current_user = Depends(require_role([0, 1]))):
    response = ai_recommendation_repo.get_aiRec_by_id(idAIRec)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI recommendation not found")
    
    assert_owner_or_admin(current_user, response[0]["iduser"])
    
    return ai_recommendation_repo.delete_aiRec(idAIRec)
