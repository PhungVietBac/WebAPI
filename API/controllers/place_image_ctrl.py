from fastapi import APIRouter, Depends, HTTPException, status
from schemas import place_image_schema
from repositories import place_image_repo
from controllers.auth_ctrl import get_current_user

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/placeimages/all", response_model=list[place_image_schema.PlaceImageResponse])
def get_place_images(current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return place_image_repo.get_place_images(skip, limit)

@router.get("/placeimages", response_model=place_image_schema.PlaceImageResponse)
def get_place_image_by_id(idImage: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    image = place_image_repo.get_place_image_by_id(idImage)
    if not image:
        raise HTTPException(status_code=404, detail="Place image not found")
    
    return image[0]

@router.get("/placeimages/", response_model=list[place_image_schema.PlaceImageResponse])
def get_place_image_by(idPlace: str, current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    image = place_image_repo.get_place_image_by_idPlace(idPlace, skip, limit)
    if not image:
        raise HTTPException(status_code=404, detail="Place image not found")
    
    return image

@router.post("/placeimages/", response_model=place_image_schema.PlaceImageResponse)
def create_place_image(placeImage: place_image_schema.PlaceImageCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_image_repo.create_place_image(placeImage)

@router.delete("/placeimages/{idImage}", response_model=dict[str, str])
def delete_place_review(idImage: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_image_repo.delete_image(idImage)
