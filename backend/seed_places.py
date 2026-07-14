import json
import re
from pathlib import Path

from database import SessionLocal
from models import Place


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_FILE = PROJECT_DIR / "서울데이터" / "서울_관광지.json"


def to_float(value):
    if value is None or value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def extract_district(addr1):
    """
    예:
    서울특별시 영등포구 노들로 221
    -> 영등포구
    """
    if not addr1:
        return None

    match = re.search(r"서울특별시\s+([가-힣]+구)", addr1)

    if match:
        return match.group(1)

    return None


def seed_places():
    if not DATA_FILE.exists():
        print(f"파일을 찾지 못했습니다: {DATA_FILE}")
        return

    db = SessionLocal()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    region = data.get("region")
    category = data.get("contentType")
    items = data.get("items", [])

    inserted_count = 0
    updated_count = 0

    for item in items:
        contentid = item.get("contentid")

        if not contentid:
            continue

        addr1 = item.get("addr1") or ""

        place_data = {
            "contentid": contentid,
            "contenttypeid": item.get("contenttypeid"),
            "region": region,
            "category": category,
            "lcls_systm1": item.get("lclsSystm1"),
            "lcls_systm2": item.get("lclsSystm2"),
            "lcls_systm3": item.get("lclsSystm3"),
            "title": item.get("title") or "제목 없음",
            "addr1": addr1,
            "addr2": item.get("addr2") or "",
            "district": extract_district(addr1),
            "zipcode": item.get("zipcode") or "",
            "tel": item.get("tel") or "",
            "lat": to_float(item.get("mapy")),
            "lng": to_float(item.get("mapx")),
            "mlevel": item.get("mlevel") or "",
            "image": item.get("firstimage") or "",
            "thumbnail": item.get("firstimage2") or "",
            "copyright_type": item.get("cpyrhtDivCd") or "",
            "source_created_time": item.get("createdtime") or "",
            "source_modified_time": item.get("modifiedtime") or "",
            "raw_json": json.dumps(item, ensure_ascii=False),
        }

        existing_place = (
            db.query(Place)
            .filter(Place.contentid == contentid)
            .first()
        )

        if existing_place:
            for key, value in place_data.items():
                setattr(existing_place, key, value)
            updated_count += 1
        else:
            db.add(Place(**place_data))
            inserted_count += 1

    db.commit()
    db.close()

    print("관광지 데이터 저장 완료")
    print(f"추가: {inserted_count}건")
    print(f"수정: {updated_count}건")


if __name__ == "__main__":
    seed_places()