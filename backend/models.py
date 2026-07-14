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
    district = Column(String, nullable=True)   # 강남구 등

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

    contentid = Column(String, nullable=False, unique=True, index=True)
    content_type_id = Column(String, nullable=True)

    category = Column(String, nullable=True)  # 관광지, 문화시설, 음식점 등
    title = Column(String, nullable=False)

    addr1 = Column(String, nullable=True)
    district = Column(String, nullable=True)

    lat = Column(Float, nullable=True)  # 위도
    lng = Column(Float, nullable=True)  # 경도

    image = Column(String, nullable=True)
    tel = Column(String, nullable=True)

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

    seq = Column(Integer, nullable=False)  # 코스 순서 1, 2, 3
    note = Column(String, nullable=True)   # 장소별 메모

    post = relationship("Post", back_populates="places")
    place = relationship("Place", back_populates="posts")

    __table_args__ = (
        UniqueConstraint("post_id", "seq", name="uq_post_seq"),
        UniqueConstraint("post_id", "place_id", name="uq_post_place"),
    )