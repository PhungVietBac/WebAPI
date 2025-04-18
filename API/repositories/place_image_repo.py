from schemas.place_image_schema import PlaceImageCreate
from fastapi import HTTPException
from repositories import place_repo
import uuid
from supabase_client import supabase

def get_place_images(skip: int, limit: int):
    return supabase.table("placeimages").select("*").range(skip, skip + limit - 1).execute().data

def get_place_image_by_id(idImage: str):
    return supabase.table("placeimages").select("*").eq("idimage", idImage).execute().data

def get_place_image_by_idPlace(idPlace: str, skip: int, limit: int):
    return supabase.table("placeimages").select("*").eq("idplace", idPlace).range(skip, skip + limit - 1).execute().data

#tạo mới
def create_place_image(placeImage: PlaceImageCreate):
    if not place_repo.get_place_by_id(placeImage.idplace):
        raise HTTPException(404, "Place not found")
    
    idImage = ""
    while not idImage or get_place_image_by_id(idImage):
        idImage =  f"IM{str(uuid.uuid4())[:4]}"

    db_place_image = {
        "idimage": idImage,
        "idplace": placeImage.idplace,
        "image": placeImage.image
    }
    
    response = supabase.table("placeimages").insert(db_place_image).execute()

    return response.data[0]

#xóa
def delete_image(image_id: str):
    if not get_place_image_by_id(image_id):
        raise HTTPException(404, "Image not found")
    
    supabase.table("placeimages").delete().eq("idimage", image_id).execute()
    return {"message": "Image deleted successfully"}
