from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_

import models
from database import get_db
import schemas

app = FastAPI()

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/api/posts")
def get_posts(
    keyword: str | None = Query(default=None),
    district: str | None = Query(default=None),
    companion: str | None = Query(default=None),
    sort: str = Query(default="latest"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=6, ge=1, le=30),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Post)
        .options(
            joinedload(models.Post.places).joinedload(models.PostPlace.place)
        )
    )

    if keyword:
        query = query.filter(
            or_(
                models.Post.title.contains(keyword),
                models.Post.content.contains(keyword),
            )
        )

    if district and district != "전체":
        query = query.filter(models.Post.district == district)

    if companion and companion != "전체":
        query = query.filter(models.Post.companion == companion)

    total = query.count()

    if sort == "views":
        query = query.order_by(models.Post.views.desc(), models.Post.id.desc())
    else:
        query = query.order_by(models.Post.id.desc())

    posts = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    result = []

    for post in posts:
        ordered_places = sorted(post.places, key=lambda item: item.seq)

        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "district": post.district,
            "companion": post.companion,
            "views": post.views,
            "created_at": post.created_at.strftime("%Y.%m.%d") if post.created_at else "",
            "place_count": len(ordered_places),
            "places": [
                {
                    "id": item.place.id,
                    "seq": item.seq,
                    "title": item.place.title,
                    "addr1": item.place.addr1,
                    "note": item.note,
                    "lat": item.place.lat,
                    "lng": item.place.lng,
                    "image": item.place.image,
                }
                for item in ordered_places
                if item.place
            ],
        })

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": result,
    }


@app.get("/api/posts/{post_id}", response_model=schemas.PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(models.Post)
        .options(selectinload(models.Post.places).selectinload(models.PostPlace.place))
        .filter(models.Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.views = (post.views or 0) + 1
    db.add(post)
    db.commit()
    db.refresh(post)

    places = sorted(post.places, key=lambda pp: pp.seq)
    place_outs = [schemas.PostPlaceOut(seq=pp.seq, note=pp.note, place=schemas.PlaceOut(
        id=pp.place.id,
        contentid=pp.place.contentid,
        category=pp.place.category,
        title=pp.place.title,
        addr1=pp.place.addr1,
        district=pp.place.district,
        lat=pp.place.lat,
        lng=pp.place.lng,
        image=pp.place.image,
        tel=pp.place.tel,
    )) for pp in places]

    return schemas.PostDetail(
        id=post.id,
        title=post.title,
        content=post.content,
        district=post.district,
        companion=post.companion,
        views=post.views,
        created_at=post.created_at,
        updated_at=post.updated_at,
        places=place_outs,
    )


@app.post("/api/posts")
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db)):
    post = models.Post(
        title=payload.title,
        content=payload.content,
        password=payload.password,
        district=payload.district,
        companion=payload.companion,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    seq = 1
    for pid in payload.place_ids:
        pp = models.PostPlace(post_id=post.id, place_id=pid, seq=seq)
        db.add(pp)
        seq += 1
    db.commit()

    return {"id": post.id}


@app.put("/api/posts/{post_id}")
def update_post(post_id: int, payload: schemas.PostUpdate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    post.title = payload.title
    post.content = payload.content
    db.add(post)

    if payload.place_ids is not None:
        db.query(models.PostPlace).filter(models.PostPlace.post_id == post.id).delete()
        db.commit()
        seq = 1
        for pid in payload.place_ids:
            pp = models.PostPlace(post_id=post.id, place_id=pid, seq=seq)
            db.add(pp)
            seq += 1

    db.commit()
    return {"id": post.id}


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, payload: schemas.PostDeleteRequest, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    db.delete(post)
    db.commit()
    return {"message": "삭제되었습니다."}