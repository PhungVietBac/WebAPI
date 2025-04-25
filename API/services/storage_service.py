from supabase_client import supabase
from fastapi import UploadFile
import uuid

async def upload_avatar(file: UploadFile) -> str:
    fileName = f"{uuid.uuid4()}_{file.filename}"
    file_data = await file.read()
    
    res = supabase.storage.from_("avatars").upload(
        path=fileName,
        file=file_data,
        file_options={
            "content-type": file.content_type,
            "upsert": "true",
            "cache-control": "3600"
        }
    )
    
    publicUrl = supabase.storage.from_("avatars").get_public_url(fileName)
    return publicUrl

def delete_old_avatar(url: str):
    if not url: return
    from urllib.parse import urlparse
    fileName = urlparse(url).path.split("/")[-1]
    
    return supabase.storage.from_("avatars").remove([fileName])