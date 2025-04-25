from fastapi import APIRouter, Depends, HTTPException, status
from schemas import review_schema
from repositories import review_repo, user_repo, trip_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin
from controllers.trip_ctrl import assert_owner_or_admin_on_trip

router = APIRouter()

# Get all reviews
@router.get("/reviews/all", response_model=list[review_schema.ReviewResponse])
def get_reviews(current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    return review_repo.get_reviews(skip, limit)

# Get a review by id
@router.get("/reviews", response_model=review_schema.ReviewResponse)
def get_review_by_id(idReview: str, current_user = Depends(require_role([0, 1]))):
    review = review_repo.get_review_by_id(idReview)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    return review[0]

# Get a review by
@router.get("/reviews/{select}", response_model=list[review_schema.ReviewResponse])
def get_review_by(select: str, lookup: str, current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    if select == "idUser":
        review = review_repo.get_review_by_user(lookup, skip, limit)
    elif select == "idTrip":
        review = review_repo.get_review_by_trip(lookup, skip, limit)
    elif select == "rating":
        try:
            value = float(lookup)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rating value")
        review = review_repo.get_review_by_rating(value, skip, limit)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    return review

# Get top reviews
@router.get("/reviews/top/", response_model=list[review_schema.ReviewResponse])
def get_best_reviews(current_user = Depends(require_role([0, 1]))):
    response = review_repo.get_best_reviews()
    
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reviews found")
    return response

# Post a new review
@router.post("/reviews/", response_model=review_schema.ReviewResponse)
def create_review(review: review_schema.ReviewCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, review.iduser)
    assert_owner_or_admin_on_trip(review.idtrip, current_user)
    
    if not user_repo.get_user_by("idUser", review.iduser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not trip_repo.get_trip_by_id(review.idtrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    return review_repo.create_review(review)

# Delete a review
@router.delete("/reviews/{idReview}", response_model=dict[str, str])
def delete_review(idReview: str, current_user = Depends(require_role([0, 1]))):
    review = get_review_by_id(idReview)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    assert_owner_or_admin(current_user, review[0]["iduser"])
    
    return review_repo.delete_review(idReview)
