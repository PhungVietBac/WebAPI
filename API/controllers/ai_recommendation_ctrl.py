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

    prompt = f"""Lập kế hoạch du lịch {ai_req.days} ngày từ {ai_req.departure} đến {ai_req.destination} cho {ai_req.people} người, bắt đầu từ ngày {ai_req.time}, với ngân sách khoảng {ai_req.money} đồng cho cả chuyến đi."""
    if ai_req.transportation:
        prompt += f" Phương tiện di chuyển chính là {ai_req.transportation}."
    if ai_req.travelStyle:
        prompt += f" Phong cách du lịch mong muốn: {ai_req.travelStyle}."
    if ai_req.interests:
        prompt += f" Sở thích của nhóm gồm: {', '.join(ai_req.interests)}."
    if ai_req.accommodation:
        prompt += f" Loại hình chỗ ở mong muốn: {ai_req.accommodation}."

    prompt += """
    Yêu cầu lập lịch trình chi tiết theo từng ngày, chia rõ theo các mốc thời gian:

    - **06:30 - 08:00:** Ăn sáng (gợi ý món và địa điểm cụ thể, giá hợp lý)
    - **08:00 - 11:30:** Hoạt động buổi sáng (tham quan, vui chơi, v.v.)
    - **11:30 - 13:30:** Ăn trưa (gợi ý nhà hàng + món ăn phù hợp với ngân sách)
    - **13:30 - 15:00:** Nghỉ trưa tại khách sạn hoặc nơi yên tĩnh
    - **15:00 - 18:00:** Hoạt động buổi chiều (tham quan, giải trí, tắm biển...)
    - **18:30 - 20:00:** Ăn tối (gợi ý nhà hàng, món ăn đặc sản)
    - **20:00 - 22:00:** Hoạt động buổi tối (mua sắm, dạo biển, xem show, v.v.)
    - **22:00:** Về lại khách sạn để nghỉ ngơi, mô tả khách sạn, tiện nghi

    Với mỗi hoạt động, cần bao gồm:
    - **Tên hoạt động**
    - **Thời gian cụ thể (giờ bắt đầu - giờ kết thúc)**
    - **Địa điểm (tên, địa chỉ, có thể kèm toạ độ GPS nếu có)**
    - **Mô tả chi tiết hoạt động**
    - **Đánh giá chất lượng (1-5 sao)**

    Tổng số hoạt động trong ngày phải lớn hơn 5. Tránh trùng lặp hoạt động giữa các ngày. Ưu tiên địa điểm phù hợp với sở thích và ngân sách của nhóm.
    """

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
            save_place_image(res['idplace'], lat, lon, activity.namePlace)
            
def save_place_image(idplace, lat, lon, name):
    images = find_images(lat, lon, name)
    if images:
        for image in images: 
            placeImage = place_image_schema.PlaceImageCreate(
                idplace=idplace,
                image=image
            )
            place_image_repo.create_place_image(placeImage)
    
def find_images(lat, lon, query):
    import requests
    from math import radians, cos, sin, asin, sqrt
    from dotenv import load_dotenv
    import os

    res = []
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * asin(sqrt(a))

    # Tìm địa điểm gần nhất
    nearby_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{lat},{lon}',
        'radius':30,
        'key': API_KEY
    }
    resp = requests.get(nearby_url, params=params).json()
    places = resp.get('results', [])

    if not places:
        print("❌ Không có địa điểm nào gần tọa độ này.")
        return find_image_by_openverse(query)
    else:
        closest = min(places, key=lambda p: haversine(
            lat, lon,
            p['geometry']['location']['lat'],
            p['geometry']['location']['lng']
        ))
        name = closest['name']
        place_id = closest['place_id']
        print(f"📍 Gần nhất: {name} ({place_id})")

        # Lấy ảnh từ place_id
        detail_url = 'https://maps.googleapis.com/maps/api/place/details/json'
        detail_params = {
            'place_id': place_id,
            'fields': 'photos',
            'key': API_KEY
        }
        detail_resp = requests.get(detail_url, params=detail_params).json()
        photos = detail_resp.get('result', {}).get('photos', [])

        if not photos:
            print("⚠️ Không có ảnh nào cho địa điểm này.")
            return find_image_by_openverse(query)
        else:
            for photo in photos:
                ref = photo.get('photo_reference')
                photo_url = (
                    f"https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth=600&photo_reference={ref}&key={API_KEY}"
                )
                # Kiểm tra URL ảnh
                check = requests.get(photo_url)
                if check.status_code == 200:
                    res.append(photo_url)
                else:
                    print(f"⚠️ Ảnh lỗi HTTP {check.status_code}, bỏ qua.")
                    
                if len(res) == 5:
                    break
                
            if len(res) == 0:
                return find_image_by_openverse(query)
            return res
    
def find_image_by_openverse(query):
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
