from fastapi import APIRouter, Depends, HTTPException, status
from schemas import place_schema, booking_schema, trip_schema
from controllers.auth_ctrl import get_current_user
from repositories import place_repo

router = APIRouter()

def check_authorization(current_user):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/places/all", response_model=list[place_schema.PlaceResponse])
def get_places(current_user = Depends(get_current_user), skip: int = 0, limit: int = 100):
    check_authorization(current_user)
    
    return place_repo.get_places(skip, limit)

@router.get("/places", response_model=place_schema.PlaceResponse)
def get_place_by_id(idPlace: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    place = place_repo.get_place_by_id(idPlace)
    if not place:
        raise HTTPException(404, "Place not found")
    
    return place[0]

@router.get("/places/{idPlace}/bookings/", response_model=list[booking_schema.BookingResponse])
def get_bookings_by_place(idPlace: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_repo.get_bookings_of_place(idPlace)

@router.get("/places/{select}", response_model=list[place_schema.PlaceResponse])
def get_place_by(select: str, lookup: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    places = place_repo.get_place_by(select, lookup)
    if not places:
        raise HTTPException(status_code=404, detail="Place not found")
    
    return places

@router.get("/places/{idPlace}/trips/", response_model=list[trip_schema.TripResponse])
def get_trips_by_place(idPlace: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_repo.get_trips_contain_place(idPlace)

@router.post("/places/", response_model=place_schema.PlaceResponse)
def create_place(place: place_schema.PlaceCreate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_repo.post_place(place)

@router.put("/places/{idPlace}", response_model=place_schema.PlaceResponse)
def update_place(idPlace: str, place: place_schema.PlaceUpdate, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_repo.update_place(idPlace, place)

@router.delete("/places/{idPlace}", response_model=dict[str, str])
def delete_place(idPlace: str, current_user = Depends(get_current_user)):
    check_authorization(current_user)
    
    return place_repo.delete_place(idPlace)

@router.get("/search/", response_model=list[place_schema.PlaceResponse])
def search_places(
    query: str,
    place_type: int = None,
    min_rating: int = None,
    current_user = Depends(get_current_user),
):
    check_authorization(current_user)
    """Search places with filters"""
    places = place_repo.search_places(
        query=query,
        place_type=place_type,
        min_rating=min_rating
    )
    
    if not places:
        raise HTTPException(status_code=404, detail="No places found")
    
    return places
