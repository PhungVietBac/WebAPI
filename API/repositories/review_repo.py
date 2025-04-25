from schemas.review_schema import ReviewCreate
import uuid
from supabase_client import supabase

def get_reviews(skip: int, limit: int):
    return supabase.table("reviews").select("*").range(skip, skip + limit - 1).execute().data

#lấy top reviews (lọc bởi rating)
def get_best_reviews():
    response = supabase.table("reviews").select("*").order("rating", desc=True).limit(5).execute().data

#Get a review by id
def get_review_by_id(idReview: str):
    return supabase.table("reviews").select("*").eq("idreview", idReview).execute().data

#Get a review
def get_review_by_user(idUser: str, skip: int, limit: int):
    return supabase.table("reviews").select("*").eq("iduser", idUser).range(skip, skip + limit - 1).execute().data

def get_review_by_trip(idTrip: str, skip: int, limit: int):
    return supabase.table("reviews").select("*").eq("idtrip", idTrip).range(skip, skip + limit - 1).execute().data

def get_review_by_rating(rating: float, skip: int, limit: int):
    return supabase.table("reviews").select("*").eq("rating", rating).range(skip, skip + limit - 1).execute().data

#tạo mới
def create_review(review: ReviewCreate):
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
    supabase.table("reviews").delete().eq("idreview", review_id).execute()
    return {"message": "Review deleted successfully"}
