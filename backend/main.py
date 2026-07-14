from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, selectinload

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


@app.get("/api/posts", response_model=list[schemas.PostListItem])
def list_posts(district: str | None = None, page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    q = db.query(models.Post)
    if district:
        q = q.filter(models.Post.district == district)
    q = q.order_by(models.Post.created_at.desc())
    offset = (page - 1) * size
    posts = q.offset(offset).limit(size).all()

    results = []
    for p in posts:
        results.append(
            schemas.PostListItem(
                id=p.id,
                title=p.title,
                district=p.district,
                views=p.views,
                created_at=p.created_at,
                has_course=(len(p.places) > 0),
            )
        )
    return results


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