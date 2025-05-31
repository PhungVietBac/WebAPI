from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Query
from schemas import ai_recommendation_schema, result, place_schema, place_image_schema
from repositories import ai_recommendation_repo, user_repo, place_repo, place_image_repo
from controllers.auth_ctrl import require_role, assert_owner_or_admin
from gemini_client import get_trip_plan
from supabase_client import supabase

router = APIRouter()

@router.get("/", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_recs(current_user = Depends(require_role([0])), skip: int = Query(0), limit: int = Query(100)):
    
    return ai_recommendation_repo.get_aiRec(skip, limit)

@router.get("/id/{idAIRec}", response_model=ai_recommendation_schema.AIRecResponse)
def get_ai_rec_by_id(idAIRec: str, current_user = Depends(require_role([0, 1]))):
    
    ai_rec = ai_recommendation_repo.get_aiRec_by_id(idAIRec)
    if not ai_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI recommendation not found")
    
    assert_owner_or_admin(current_user, ai_rec[0]["iduser"])
    
    return ai_rec[0]

@router.get("/{idUser}", response_model=list[ai_recommendation_schema.AIRecResponse])
def get_ai_rec_by_user(idUser: str, current_user = Depends(require_role([0, 1])), skip: int = Query(0), limit: int = Query(100)): 
    assert_owner_or_admin(current_user, idUser)
    
    if not user_repo.get_user_by_id(idUser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    response = ai_recommendation_repo.get_aiRec_by_user(idUser, skip, limit)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No AI recommendations found")
    
    return response

@router.post("/", response_model=ai_recommendation_schema.AIRecResponse)
def create_ai_rec(ai_rec: ai_recommendation_schema.AIRecCreate, current_user = Depends(require_role([0, 1]))):
    assert_owner_or_admin(current_user, ai_rec.iduser)
    
    if not user_repo.get_user_by_id(ai_rec.iduser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return ai_recommendation_repo.create_aiRec(ai_rec)

@router.delete("/{idAIRec}", response_model=dict[str, str])
def delete_ai_rec(idAIRec: str, current_user = Depends(require_role([0, 1]))):
    response = ai_recommendation_repo.get_aiRec_by_id(idAIRec)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI recommendation not found")
    
    assert_owner_or_admin(current_user, response[0]["iduser"])
    
    return ai_recommendation_repo.delete_aiRec(idAIRec)

@router.post("/generate-trip", response_model=result.TripPlan)
async def generate_trip(ai_req: ai_recommendation_schema.AIRequest, background_tasks: BackgroundTasks, current_user = Depends(require_role([0, 1]))):

    prompt = f"Lên kế hoạch du lịch {ai_req.days} ngày từ {ai_req.departure} đến {ai_req.destination} cho {ai_req.people} người bắt đầu từ ngày {ai_req.time} với ngân sách là {ai_req.money} đồng"
    if not ai_req.transportation: 
        prompt += f" bằng {ai_req.transportation},"
    if ai_req.travelStyle:
        prompt += f" với phong cách du lịch {ai_req.travelStyle},"
    if ai_req.interests:
        prompt += f" với sở thích {', '.join(ai_req.interests)},"
    if ai_req.accommodation:
        prompt += f" với chỗ ở {ai_req.accommodation},"
    try:
        trip_plan = get_trip_plan(prompt)
        background_tasks.add_task(save_place, trip_plan)
        return trip_plan
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gemini API error: {str(e)}")
    
async def save_place(trip: result.TripPlan):
    for day in trip.parameters.days:
        for activity in day.activities:
            lon, lat = activity.lon, activity.lat
            dup_resp = supabase.rpc(
                "exists_within_radius",
                {"lon": lon, "lat": lat, "radius": 50}
            ).execute()
            
            if dup_resp.data:
                print(f"Skip duplicate: {activity.namePlace}")  
                continue
            
            place = place_schema.PlaceCreate(
                name=activity.namePlace,
                country="Việt Nam",
                city=activity.city,
                province=activity.province,
                address=activity.address,
                description=activity.description,
                rating=activity.rating,
                type=None,
                lat=lat,
                lon=lon
            )
            res = place_repo.post_place(place)
            save_place_image(res['idplace'], activity.namePlace)
            
def save_place_image(idplace, name):
    images = find_images(name)
    if images:
        for image in images: 
            placeImage = place_image_schema.PlaceImageCreate(
                idplace=idplace,
                image=image
            )
            place_image_repo.create_place_image(placeImage)
    
def find_images(query: str):
    import requests
    res = []
    url = f'https://api.openverse.engineering/v1/images?q={query}&page=1&format=json'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            count = len(data['results'])
            if 'results' in data and count > 0:
                idx = 0
                while idx < count:
                    res.append(data['results'][idx]['url'])
                    idx = idx + 1
                    if len(res) == 5:
                        break
                return res
            else:
                print("No result for this keyword.")
        else:
            print(f"Fail request: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error request API: {e}")
    except ValueError as e:
        print(f"Error parse JSON: {e}")
