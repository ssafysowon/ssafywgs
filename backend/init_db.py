from database import Base, engine
import models


def init_db():
    Base.metadata.create_all(bind=engine)
    print("SQLite DB 테이블 생성 완료: localhub.db")


if __name__ == "__main__":
    init_db()