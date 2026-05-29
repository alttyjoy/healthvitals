from fastapi import APIRouter, HTTPException, Request

from config import db, CONTENT_PAGES, TRANSLATIONS
from models import BlogPostRequest
from utils import get_admin_user
from datetime import datetime, timezone

router = APIRouter()

@router.get("/content/{page_key}")
async def get_content_page(page_key: str):
    custom = await db.content_pages.find_one({"key": page_key}, {"_id": 0})
    if custom:
        return custom
    if page_key in CONTENT_PAGES:
        return CONTENT_PAGES[page_key]
    raise HTTPException(status_code=404, detail="Page not found")

@router.get("/content")
async def list_content_pages():
    pages = list(CONTENT_PAGES.keys())
    custom = await db.content_pages.find({}, {"_id": 0, "key": 1, "title": 1}).to_list(50)
    for c in custom:
        if c["key"] not in pages:
            pages.append(c["key"])
    return {"pages": pages}

@router.get("/translations/{lang}")
async def get_translations(lang: str):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])

@router.get("/languages")
async def list_languages():
    return [
        {"code": "en", "name": "English", "native": "English"},
        {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
        {"code": "te", "name": "Telugu", "native": "తెలుగు"},
    ]

@router.get("/blog")
async def list_blog_posts(published_only: bool = True):
    query = {"published": True} if published_only else {}
    posts = await db.blog_posts.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return posts

@router.get("/blog/{slug}")
async def get_blog_post(slug: str):
    post = await db.blog_posts.find_one({"slug": slug}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post

@router.post("/admin/blog")
async def create_blog_post(req: BlogPostRequest, request: Request):
    await get_admin_user(request)
    doc = req.dict()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.blog_posts.update_one({"slug": req.slug}, {"$set": doc}, upsert=True)
    return {"message": "Blog post saved"}

@router.put("/admin/blog/{slug}")
async def update_blog_post(slug: str, req: BlogPostRequest, request: Request):
    await get_admin_user(request)
    doc = req.dict()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.blog_posts.update_one({"slug": slug}, {"$set": doc})
    return {"message": "Blog post updated"}

@router.delete("/admin/blog/{slug}")
async def delete_blog_post(slug: str, request: Request):
    await get_admin_user(request)
    await db.blog_posts.delete_one({"slug": slug})
    return {"message": "Blog post deleted"}
