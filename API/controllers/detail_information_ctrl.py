from fastapi import APIRouter, Depends, HTTPException, status
from schemas import detail_information_schema
from repositories import detail_information_repo, trip_repo, place_repo
from controllers.auth_ctrl import require_role
from controllers.trip_ctrl import assert_owner_or_admin_on_trip
from datetime import datetime

router = APIRouter()

@router.get("/details/all", response_model=list[detail_information_schema.DetailResponse])
def get_details(current_user = Depends(require_role([0])), skip: int = 0, limit: int = 100):
    
    return detail_information_repo.get_details(skip, limit)

@router.get("/details", response_model=detail_information_schema.DetailResponse)
def get_detail_by_id(idDetail: str, current_user = Depends(require_role([0, 1]))):
    
    detail = detail_information_repo.get_detail_information_by_id(idDetail)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail information not found")
    
    assert_owner_or_admin_on_trip(detail[0]["idtrip"], current_user)
    
    return detail[0]

@router.get("/details/{select}", response_model=list[detail_information_schema.DetailResponse])
def get_detail_by(select: str, lookup: str, current_user = Depends(require_role([0, 1])), skip: int = 0, limit: int = 100):
    if select == "idPlace":
        details = detail_information_repo.get_detail_by_idPlace(lookup, skip, limit)
    elif select == "idTrip":
        details = detail_information_repo.get_detail_by_idTrip(lookup, skip, limit)
    elif select == "startTime":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        details = detail_information_repo.get_detail_by_startTime(time, skip, limit)
    elif select == "endTime":
        try:
            time = datetime.strptime(lookup, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use 'dd/mm/yyyy hh:mm:ss'")
        details = detail_information_repo.get_detail_by_endTime(time, skip, limit)
    else:    
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid select parameter")
    
    if current_user["role"] != 0:
        details = [
            d for d in details
            if current_user["iduser"] in trip_repo.get_members_of_trip(d["idtrip"])
        ]

    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail information not found")
    
    return details

@router.post("/details/", response_model=detail_information_schema.DetailResponse)
def create_detail(detail: detail_information_schema.DetailCreate, current_user = Depends(require_role([0, 1]))):
    if not trip_repo.get_trip_by_id(detail.idtrip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    assert_owner_or_admin_on_trip(detail.idtrip, current_user)
    
    if not place_repo.get_place_by_id(detail.idplace):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    
    return detail_information_repo.post_detail_information(detail)

@router.put("/details/{idDetail}", response_model=detail_information_schema.DetailResponse)
def update_detail(idDetail: str, detail: detail_information_schema.DetailUpdate, current_user = Depends(require_role([0, 1]))):
    response = detail_information_repo.get_detail_information_by_id(idDetail)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail information not found")
    
    assert_owner_or_admin_on_trip(response[0]["idtrip"], current_user)
    
    if not trip_repo.get_trip_by_id(detail.idtrip):
        raise HTTPException(404, "Trip not found")
    
    assert_owner_or_admin_on_trip(detail.idtrip, current_user)
    
    if not place_repo.get_place_by_id(detail.idplace):
        raise HTTPException(404, "Place not found")
    
    return detail_information_repo.update_detail_information(idDetail, detail)

@router.delete("/details/{idDetail}", response_model=dict[str, str])
def delete_detail(idDetail: str, current_user = Depends(require_role([0, 1]))):
    response = detail_information_repo.get_detail_information_by_id(idDetail)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detail information not found")
    
    assert_owner_or_admin_on_trip(response[0]["idtrip"], current_user)
    
    return detail_information_repo.delete_detail_information(idDetail)
    