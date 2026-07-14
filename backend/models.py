from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String, nullable=False)

    companion = Column(String, nullable=True)  # 연인, 친구, 가족, 혼자
    district = Column(String, nullable=True)   # 강남구, 종로구 등

    views = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    places = relationship(
        "PostPlace",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)

    # TourAPI 원본 식별값
    contentid = Column(String, nullable=False, unique=True, index=True)
    contenttypeid = Column(String, nullable=True)

    # 분류 정보
    region = Column(String, nullable=True)       # 서울
    category = Column(String, nullable=True)     # 관광지
    lcls_systm1 = Column(String, nullable=True)
    lcls_systm2 = Column(String, nullable=True)
    lcls_systm3 = Column(String, nullable=True)

    # 기본 정보
    title = Column(String, nullable=False)
    addr1 = Column(String, nullable=True)
    addr2 = Column(String, nullable=True)
    district = Column(String, nullable=True)     # 주소에서 추출한 구 이름
    zipcode = Column(String, nullable=True)
    tel = Column(String, nullable=True)

    # 지도 정보
    lat = Column(Float, nullable=True)           # 위도 = mapy
    lng = Column(Float, nullable=True)           # 경도 = mapx
    mlevel = Column(String, nullable=True)

    # 이미지 정보
    image = Column(String, nullable=True)        # firstimage
    thumbnail = Column(String, nullable=True)    # firstimage2
    copyright_type = Column(String, nullable=True)  # cpyrhtDivCd

    # 원본 데이터 시간
    source_created_time = Column(String, nullable=True)   # createdtime
    source_modified_time = Column(String, nullable=True)  # modifiedtime

    # 원본 JSON 보관용
    raw_json = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    posts = relationship(
        "PostPlace",
        back_populates="place",
        cascade="all, delete-orphan",
    )


class PostPlace(Base):
    __tablename__ = "post_places"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)

    seq = Column(Integer, nullable=False)  # 코스 순서: 1, 2, 3
    note = Column(String, nullable=True)   # 장소별 메모

    post = relationship("Post", back_populates="places")
    place = relationship("Place", back_populates="posts")

    __table_args__ = (
        UniqueConstraint("post_id", "seq", name="uq_post_seq"),
        UniqueConstraint("post_id", "place_id", name="uq_post_place"),
    )