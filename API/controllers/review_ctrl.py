from fastapi import APIRouter, Depends, HTTPException, status
from schemas import review_schema
from repositories import review_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

# Get all reviews
@router.get("/reviews/all", response_model=list[review_schema.ReviewResponse])
def get_reviews(current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return review_repo.get_reviews(skip, limit)

# Get a review by id
@router.get("/reviews", response_model=review_schema.ReviewResponse)
def get_review_by_id(idReview: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    review = review_repo.get_review_by_id(idReview)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return review[0]

# Get a review by
@router.get("/reviews/{select}", response_model=list[review_schema.ReviewResponse])
def get_review_by(select: str, lookup: str, current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    review = review_repo.get_review_by(select, lookup, skip, limit)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return review

# Get top reviews
@router.get("/reviews/top/", response_model=list[review_schema.ReviewResponse])
def get_best_reviews(current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return review_repo.get_best_reviews()

# Post a new review
@router.post("/reviews/", response_model=review_schema.ReviewResponse)
def create_review(review: review_schema.ReviewCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return review_repo.create_review(review)

# Delete a review
@router.delete("/reviews/{idReview}", response_model=dict[str, str])
def delete_review(idReview: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return review_repo.delete_review(idReview)
