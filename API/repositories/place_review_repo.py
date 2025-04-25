from schemas.place_review_schema import PlaceReviewCreate
import uuid
from supabase_client import supabase

def get_place_reviews(skip: int, limit: int):
    return supabase.table("placereviews").select("*").range(skip, skip + limit - 1).execute().data

#lấy top placereviews (lọc bởi rating)
def get_best_place_reviews():
    return supabase.table("placereviews").select("*").order("rating", desc=True).limit(5).execute().data

def get_place_review_by_id(idReview: str):
    return supabase.table("placereviews").select("*").eq("idreview", idReview).execute().data

def get_place_review_by_name(name: str, skip: int, limit: int):
    return supabase.table("placereviews").select("*").eq("name", name).range(skip, skip + limit - 1).execute().data

def get_place_review_by_place(idPlace: str, skip: int, limit: int):
    return supabase.table("placereviews").select("*").eq("idplace", idPlace).range(skip, skip + limit - 1).execute().data

def get_place_review_by_rating(rating: float, skip: int, limit: int):
    return supabase.table("placereviews").select("*").eq("rating", rating).range(skip, skip + limit - 1).execute().data

#tạo mới
def create_place_review(placeReview: PlaceReviewCreate):
    idReview = ""
    while not idReview or get_place_review_by_id(idReview):
        idReview =  f"RV{str(uuid.uuid4())[:4]}"

    db_place_review = {
        "idreview": idReview,
        "idplace": placeReview.idplace,
        "name": placeReview.name,
        "comment": placeReview.comment,
        "rating": placeReview.rating
    }
    
    response = supabase.table("placereviews").insert(db_place_review).execute()

    return response.data[0]

#xóa
def delete_review(place_review_id: str):
    supabase.table("placereviews").delete().eq("idreview", place_review_id).execute()
    return {"message": "Place review deleted successfully"}
