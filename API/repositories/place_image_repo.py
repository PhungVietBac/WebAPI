from schemas.place_image_schema import PlaceImageCreate
import uuid
from supabase_client import supabase

def get_place_images(skip: int, limit: int):
    return supabase.table("placeimages").select("*").range(skip, skip + limit - 1).execute().data

def get_place_image_by_id(idImage: str):
    return supabase.table("placeimages").select("*").eq("idimage", idImage).limit(1).execute().data

def get_place_image_by_idPlace(idPlace: str, skip: int, limit: int):
    return supabase.table("placeimages").select("*").eq("idplace", idPlace).range(skip, skip + limit - 1).execute().data

#tạo mới
def create_place_image(placeImage: PlaceImageCreate):
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
    supabase.table("placeimages").delete().eq("idimage", image_id).execute()
    return {"message": "Image deleted successfully"}
