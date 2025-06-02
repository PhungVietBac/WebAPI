from fastapi import APIRouter, Query
from fastapi.responses import Response
import httpx
import os
import hashlib
from datetime import datetime
import time
from dotenv import load_dotenv
import threading

router = APIRouter()

load_dotenv()
CACHE_DIR = "cache"
CACHE_EXPIRY_SECONDS = int(os.getenv("CACHE_EXPIRY_SECONDS"))

os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url: str):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    current_date = datetime.now()
    year_month_day = current_date.strftime("%Y/%m/%d")
    
    cache_path = os.path.join(CACHE_DIR, year_month_day)
    os.makedirs(cache_path, exist_ok=True)
    
    return os.path.join(cache_path, url_hash)

def clean_old_cache():
    now = time.time()
    
    for root, dirs, files in os.walk(CACHE_DIR, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.exists(file_path):
                file_mtime = os.path.getmtime(file_path)
                if now - file_mtime > CACHE_EXPIRY_SECONDS:
                    try:
                        os.remove(file_path)
                        print(f"✅ Deleted old cache file: {filename}")
                    except Exception as e:
                        print(f"⚠️ Unable to delete {filename}: {e}")
                
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    print(f"🧹 Deleted empty folder: {dir_path}")
                except Exception as e:
                    print(f"⚠️ Unable to delete folder {dir_path}: {e}")
                    
def start_cache_cleaner(interval_seconds=1800):
    def cleaner():
        while True:
            print("🧹 Cleaning...")
            clean_old_cache()
            time.sleep(interval_seconds)
            
    thread = threading.Thread(target=cleaner, daemon=True)
    thread.start()

@router.get("/")
async def proxy_image(url: str = Query(...)):
    cache_path = get_cache_path(url)
    meta_path = cache_path + ".meta"

    # Serve cached
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            content = f.read()
        content_type = "image/jpeg"
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                content_type = f.read().strip()
        return Response(content=content, media_type=content_type)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            # First try: download whole image into memory
            resp = await client.get(url)
            if resp.status_code != 200:
                return Response(status_code=resp.status_code)

            content_type = resp.headers.get("Content-Type", "image/jpeg")
            try:
                content = await resp.aread()
            except Exception as e:
                print("⚠️ aread() failed:", e)
                raise e  # fallback to stream below

            with open(cache_path, "wb") as f:
                f.write(content)
            with open(meta_path, "w") as f:
                f.write(content_type)

            return Response(content=content, media_type=content_type)

        except Exception as e1:
            # Fallback: stream content if full read fails
            print("🔁 Fallback to stream due to:", e1)
            try:
                async with client.stream("GET", url) as resp:
                    if resp.status_code != 200:
                        return Response(status_code=resp.status_code)

                    content_type = resp.headers.get("Content-Type", "image/jpeg")
                    with open(cache_path, "wb") as f:
                        async for chunk in resp.aiter_bytes():
                            f.write(chunk)

                    with open(meta_path, "w") as f:
                        f.write(content_type)

                with open(cache_path, "rb") as f:
                    return Response(content=f.read(), media_type=content_type)
            except Exception as e2:
                print("❌ Proxy error (stream fallback):", e2)
                return Response(status_code=502, content="Download failed")
