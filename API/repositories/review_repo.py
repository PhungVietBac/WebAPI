from schemas.review_schema import ReviewCreate
from fastapi import HTTPException
from repositories import user_repo
from repositories import trip_repo
import uuid
from supabase_client import supabase

def get_reviews(skip: int, limit: int):
    return supabase.table("reviews").select("*").range(skip, skip + limit - 1).execute().data

#lấy top reviews (lọc bởi rating)
def get_best_reviews():
    response = supabase.table("reviews").select("*").order("rating", desc=True).limit(5).execute().data
    
    if not response:
        raise HTTPException(404, "No reviews found")
    return response

#Get a review by id
def get_review_by_id(idReview: str):
    return supabase.table("reviews").select("*").eq("idreview", idReview).execute().data

#Get a review
def get_review_by(select: str, lookup: str, skip: int, limit: int):
    if select == "idUser":
        return supabase.table("reviews").select("*").eq("iduser", lookup).range(skip, skip + limit - 1).execute().data
    elif select == "idTrip":
        return supabase.table("reviews").select("*").eq("idtrip", lookup).range(skip, skip + limit - 1).execute().data
    elif select == "rating":
        try:
            value = float(lookup)
        except ValueError:
            raise HTTPException(400, "Invalid rating value")
        return supabase.table("reviews").select("*").eq("rating", value).range(skip, skip + limit - 1).execute().data
    else:
        raise HTTPException(400, "Bad Request")

#tạo mới
def create_review(review: ReviewCreate):
    if not user_repo.get_user_by("idUser", review.iduser):
        raise HTTPException(404, "User not found")
    
    if not trip_repo.get_trip_by_id(review.idtrip):
        raise HTTPException(404, "Trip not found")
    
    idReview = ""
    while not idReview or get_review_by_id(idReview):
        idReview =  f"RV{str(uuid.uuid4())[:4]}"

    db_review = {
        "idreview": idReview,
        "idtrip": review.idtrip,
        "iduser": review.iduser,
        "comment": review.comment,
        "rating": review.rating
    }
    
    response = supabase.table("reviews").insert(db_review).execute()

    return response.data[0]

#xóa
def delete_review(review_id: str):
    review = get_review_by_id(review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    
    supabase.table("reviews").delete().eq("idreview", review_id).execute()
    return {"message": "Review deleted successfully"}
