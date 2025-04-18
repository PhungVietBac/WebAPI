from schemas.place_review_schema import PlaceReviewCreate
from fastapi import HTTPException
from repositories import place_repo
import uuid
from supabase_client import supabase

def get_place_reviews(skip: int, limit: int):
    return supabase.table("placereviews").select("*").range(skip, skip + limit - 1).execute().data

#lấy top placereviews (lọc bởi rating)
def get_best_place_reviews():
    response = supabase.table("placereviews").select("*").order("rating", desc=True).limit(5).execute().data
    
    if not response:
        raise HTTPException(404, "No place reviews found")
    return response

def get_place_review_by_id(idReview: str):
    return supabase.table("placereviews").select("*").eq("idreview", idReview).execute().data

def get_place_review_by(select: str, lookup: str, skip: int, limit: int):
    if select == "name":
        return supabase.table("placereviews").select("*").eq("name", lookup).range(skip, skip + limit - 1).execute().data
    elif select == "idPlace":
        return supabase.table("placereviews").select("*").eq("idplace", lookup).range(skip, skip + limit - 1).execute().data
    elif select == "rating":
        try:
            value = float(lookup)
        except ValueError:
            raise HTTPException(400, "Invalid rating value")
        return supabase.table("placereviews").select("*").eq("rating", value).range(skip, skip + limit - 1).execute().data
    else:
        raise HTTPException(400, "Bad Request")

#tạo mới
def create_place_review(placeReview: PlaceReviewCreate):
    if not place_repo.get_place_by_id(placeReview.idplace):
        raise HTTPException(404, "Place not found")
    
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
    if not get_place_review_by_id(place_review_id):
        raise HTTPException(404, "Place review not found")
    
    supabase.table("placereviews").delete().eq("idreview", place_review_id).execute()
    return {"message": "Place review deleted successfully"}
