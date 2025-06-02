import requests
from math import radians, cos, sin, asin, sqrt

API_KEY = 'AIzaSyAGoDXGDNYEzqAxHkkAHjow012yDb-SbJI'
lat, lon = 10.86407175851326, 106.8024327334087

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
    else:
        for i, photo in enumerate(photos[:5]):
            ref = photo.get('photo_reference')
            photo_url = (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=600&photo_reference={ref}&key={API_KEY}"
            )
            # Kiểm tra URL ảnh
            check = requests.get(photo_url)
            if check.status_code == 200:
                print(f"🖼️ Ảnh {i+1}: {photo_url}")
            else:
                print(f"⚠️ Ảnh {i+1} lỗi HTTP {check.status_code}, bỏ qua.")
