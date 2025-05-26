from fastapi import APIRouter, Depends, HTTPException, status
from schemas import place_review_schema
from repositories import place_review_repo, place_repo, user_repo
from controllers.auth_ctrl import require_role

router = APIRouter()

@router.get("/placereviews/all", response_model=list[place_review_schema.PlaceReviewResponse])
def get_place_reviews(current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    return place_review_repo.get_place_reviews(skip, limit)

@router.get("/placereviews", response_model=place_review_schema.PlaceReviewResponse)
def get_place_review_by_id(idReview: str, current_user = Depends(require_role([0, 1]))):
    review = place_review_repo.get_place_review_by_id(idReview)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place review not found")
    
    return review[0]

@router.get("/placereviews/{select}", response_model=list[place_review_schema.PlaceReviewResponse], summary="Get place review by name, idPlace, rating")
def get_place_review_by(select: str, lookup: str, current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    if select == "name":
        review = place_review_repo.get_place_review_by_name(lookup, skip, limit)
    elif select == "idPlace":
        review = place_review_repo.get_place_review_by_place(lookup, skip, limit)
    elif select == "rating":
        try:
            value = float(lookup)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rating value")
        review = place_review_repo.get_place_review_by_rating(value, skip, limit)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place review not found")
    
    return review

# Get top reviews
@router.get("/placereviews/top/", response_model=list[place_review_schema.PlaceReviewResponse])
def get_best_place_reviews(current_user = Depends(require_role([0, 1]))):
    response = place_review_repo.get_best_place_reviews()

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No place reviews found")
    return response

# Post a new review
@router.post("/placereviews/", response_model=place_review_schema.PlaceReviewResponse)
def create_place_review(placeReview: place_review_schema.PlaceReviewCreate, current_user = Depends(require_role([0, 1]))):
    if not place_repo.get_place_by_id(placeReview.idplace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    return place_review_repo.create_place_review(placeReview)

# Delete a review
@router.delete("/placereviews/{idReview}", response_model=dict[str, str])
def delete_place_review(idReview: str, current_user = Depends(require_role([0, 1]))):
    review = place_review_repo.get_place_review_by_id(idReview)
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place review not found")
    
    user = user_repo.get_user_by_id(current_user["iduser"])
    
    if current_user["role"] != 0 or user[0]["username"] != review[0]["name"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    
    return place_review_repo.delete_review(idReview)
