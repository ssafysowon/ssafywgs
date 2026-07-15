from pydantic import BaseModel
from datetime import datetime

class PlaceOut(BaseModel):
    id: int
    contentid: str
    category: str | None
    title: str
    addr1: str | None
    district: str | None
    lat: float | None
    lng: float | None
    image: str | None
    tel: str | None
    class Config:
        from_attributes = True

class PostPlaceOut(BaseModel):
    seq: int
    note: str | None
    place: PlaceOut
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    content: str
    password: str
    time: str | None = None
    district: str | None = None
    companion: str | None = None
    place_ids: list[int]   # 순서대로 온 place id 배열

class PostUpdate(BaseModel):
    title: str
    content: str
    password: str
    time: str | None = None
    district: str | None = None
    companion: str | None = None
    place_ids: list[int] | None = None

class PostDeleteRequest(BaseModel):
    password: str

class PostListItem(BaseModel):
    id: int
    title: str
    time: str | None = None
    district: str | None
    views: int
    created_at: datetime
    has_course: bool       # place가 1개 이상 있는지
    class Config:
        from_attributes = True

class PostDetail(BaseModel):
    id: int
    title: str
    content: str
    time: str | None = None
    district: str | None
    companion: str | None
    views: int
    created_at: datetime
    updated_at: datetime | None
    places: list[PostPlaceOut]
    class Config:
        from_attributes = True
