from fastapi import APIRouter, Depends, HTTPException, status
from schemas import detail_information_schema
from repositories import detail_information_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/details/all", response_model=list[detail_information_schema.DetailResponse])
def get_details(current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return detail_information_repo.get_details(skip, limit)

@router.get("/details", response_model=detail_information_schema.DetailResponse)
def get_detail_by_id(idDetail: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    detail = detail_information_repo.get_detail_information_by_id(idDetail)
    if not detail:
        raise HTTPException(404, "Detail information not found")
    
    return detail[0]

@router.get("/details/{select}", response_model=list[detail_information_schema.DetailResponse])
def get_detail_by(select: str, lookup: str, current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    details = detail_information_repo.get_detail_by(select, lookup, skip, limit)
    if not details:
        raise HTTPException(404, "Detail information not found")
    
    return details

@router.post("/details/", response_model=detail_information_schema.DetailResponse)
def create_detail(detail: detail_information_schema.DetailCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return detail_information_repo.post_detail_information(detail)

@router.put("/details/{idDetail}", response_model=detail_information_schema.DetailResponse)
def update_detail(idDetail: str, detail: detail_information_schema.DetailUpdate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return detail_information_repo.update_detail_information(idDetail, detail)

@router.delete("/details/{idDetail}", response_model=dict[str, str])
def delete_detail(idDetail: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return detail_information_repo.delete_detail_information(idDetail)
    