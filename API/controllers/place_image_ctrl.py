from fastapi import APIRouter, Depends, HTTPException, status
from schemas import place_image_schema
from repositories import place_image_repo, place_repo
from controllers.auth_ctrl import require_role

router = APIRouter()

@router.get("/placeimages/all", response_model=list[place_image_schema.PlaceImageResponse])
def get_place_images(current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    return place_image_repo.get_place_images(skip, limit)

@router.get("/placeimages", response_model=place_image_schema.PlaceImageResponse)
def get_place_image_by_id(idImage: str, current_user = Depends(require_role([0, 1]))):
    image = place_image_repo.get_place_image_by_id(idImage)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place image not found")
    
    return image[0]

@router.get("/placeimages/{idPLace}", response_model=list[place_image_schema.PlaceImageResponse])
def get_place_image_by_place(idPlace: str, current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    image = place_image_repo.get_place_image_by_idPlace(idPlace, skip, limit)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place image not found")
    
    return image

@router.post("/placeimages/", response_model=place_image_schema.PlaceImageResponse)
def create_place_image(placeImage: place_image_schema.PlaceImageCreate, current_user = Depends(require_role([0]))):
    if not place_repo.get_place_by_id(placeImage.idplace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    return place_image_repo.create_place_image(placeImage)

@router.delete("/placeimages/{idImage}", response_model=dict[str, str])
def delete_place_review(idImage: str, current_user = Depends(require_role([0]))):
    if not place_image_repo.get_place_image_by_id(idImage):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    
    return place_image_repo.delete_image(idImage)
