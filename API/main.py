from fastapi import FastAPI
from controllers import review_ctrl, trip_ctrl, trip_member_ctrl, user_ctrl, auth_ctrl, booking_ctrl, notification_ctrl, friend_ctrl, ai_recommendation_ctrl, detail_information_ctrl, place_ctrl, detail_booking_ctrl, place_image_ctrl, place_review_ctrl, proxy_image
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.middleware("http")
async def echo_localhost_cors(request, call_next):
    origin = request.headers.get("origin")
    response = await call_next(request)
    if origin and origin.startswith("http://localhost"):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS,PUT,DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response


proxy_image.start_cache_cleaner()

app.include_router(auth_ctrl.router, prefix="/api/v1", tags=["auth"])
app.include_router(user_ctrl.router, prefix="/api/v1", tags=["users"])
app.include_router(friend_ctrl.router, prefix="/api/v1", tags=["friends"])
app.include_router(notification_ctrl.router, prefix="/api/v1", tags=["notifications"])
app.include_router(trip_ctrl.router, prefix="/api/v1", tags=["trips"])
app.include_router(trip_member_ctrl.router, prefix="/api/v1", tags=["trip_members"])
app.include_router(place_ctrl.router, prefix="/api/v1", tags=["places"])
app.include_router(detail_information_ctrl.router, prefix="/api/v1", tags=["detail_informations"])
app.include_router(review_ctrl.router, prefix="/api/v1", tags=["reviews"])
app.include_router(booking_ctrl.router, prefix="/api/v1", tags=["bookings"])
app.include_router(detail_booking_ctrl.router, prefix="/api/v1", tags=["detail_bookings"])
app.include_router(ai_recommendation_ctrl.router, prefix="/api/v1", tags=["ai_recommendations"])
app.include_router(place_image_ctrl.router, prefix="/api/v1", tags=["place_images"])
app.include_router(place_review_ctrl.router, prefix="/api/v1", tags=["place_reviews"])
app.include_router(proxy_image.router, prefix="/api/v1", tags=["proxy_image"])