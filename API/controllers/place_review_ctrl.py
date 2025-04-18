from fastapi import APIRouter, Depends, HTTPException, status
from schemas import place_review_schema
from repositories import place_review_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/placereviews/all", response_model=list[place_review_schema.PlaceReviewResponse])
def get_place_reviews(current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return place_review_repo.get_place_reviews(skip, limit)

@router.get("/placereviews", response_model=place_review_schema.PlaceReviewResponse)
def get_place_review_by_id(idReview: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    review = place_review_repo.get_place_review_by_id(idReview)
    if not review:
        raise HTTPException(status_code=404, detail="Place review not found")
    
    return review[0]

@router.get("/placereviews/{select}", response_model=list[place_review_schema.PlaceReviewResponse])
def get_place_review_by(select: str, lookup: str, current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    review = place_review_repo.get_place_review_by(select, lookup, skip, limit)
    if not review:
        raise HTTPException(status_code=404, detail="Place review not found")
    
    return review

# Get top reviews
@router.get("/placereviews/top/", response_model=list[place_review_schema.PlaceReviewResponse])
def get_best_place_reviews(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_review_repo.get_best_place_reviews()

# Post a new review
@router.post("/placereviews/", response_model=place_review_schema.PlaceReviewResponse)
def create_place_review(placeReview: place_review_schema.PlaceReviewCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_review_repo.create_place_review(placeReview)

# Delete a review
@router.delete("/placereviews/{idReview}", response_model=dict[str, str])
def delete_place_review(idReview: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_review_repo.delete_review(idReview)
