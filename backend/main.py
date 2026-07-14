from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import models
from database import get_db

app = FastAPI()


@app.get("/")
def root():
    return {"message": "LocalHub backend is running"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/places")
def get_places(
    district: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(models.Place)

    if district:
        query = query.filter(models.Place.district == district)

    places = query.limit(limit).all()

    return [
        {
            "id": place.id,
            "contentid": place.contentid,
            "contenttypeid": place.contenttypeid,
            "region": place.region,
            "category": place.category,
            "title": place.title,
            "addr1": place.addr1,
            "addr2": place.addr2,
            "district": place.district,
            "zipcode": place.zipcode,
            "tel": place.tel,
            "lat": place.lat,
            "lng": place.lng,
            "image": place.image,
            "thumbnail": place.thumbnail,
            "copyright_type": place.copyright_type,
        }
        for place in places
    ]


@app.get("/api/places/{place_id}")
def get_place_detail(
    place_id: int,
    db: Session = Depends(get_db),
):
    place = (
        db.query(models.Place)
        .filter(models.Place.id == place_id)
        .first()
    )

    if not place:
        return {"message": "해당 관광지를 찾을 수 없습니다."}

    return {
        "id": place.id,
        "contentid": place.contentid,
        "contenttypeid": place.contenttypeid,
        "region": place.region,
        "category": place.category,
        "title": place.title,
        "addr1": place.addr1,
        "addr2": place.addr2,
        "district": place.district,
        "zipcode": place.zipcode,
        "tel": place.tel,
        "lat": place.lat,
        "lng": place.lng,
        "image": place.image,
        "thumbnail": place.thumbnail,
        "lcls_systm1": place.lcls_systm1,
        "lcls_systm2": place.lcls_systm2,
        "lcls_systm3": place.lcls_systm3,
        "source_created_time": place.source_created_time,
        "source_modified_time": place.source_modified_time,
    }