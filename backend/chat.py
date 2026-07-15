import os
import re
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

# Router 사용 (app에 의존하지 않음)
router = APIRouter()

# .env 로드 (backend/.env 를 우선 사용)
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger("localhub.chat")
logging.basicConfig(level=logging.INFO)

START_POINT = {"name": "SSAFY 역삼캠퍼스", "lat": 37.5009, "lng": 127.0369}

def _safe_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
        return None


def _extract_ids_and_notes(raw_places):
    ids = []
    notes = {}
    if not isinstance(raw_places, list):
        return ids, notes
    for item in raw_places:
        if isinstance(item, dict):
            pid = item.get("id")
            note = item.get("note", "")
        else:
            pid = item
            note = ""
        try:
            pid_int = int(pid)
        except Exception:
            continue
        ids.append(pid_int)
        notes[pid_int] = note
    return ids, notes

def _build_candidate_text(candidates):
    lines = []
    for p in candidates:
        title = (p.title or "").replace("\n", " ")
        addr = (p.addr1 or "").replace("\n", " ")
        cat = p.category or ""
        lines.append(f"{p.id}|{title}|{cat}|{addr}|{p.lat or ''}|{p.lng or ''}")
    return "\n".join(lines)


@router.post("/api/course/generate")
def generate_course(payload: dict = Body(...), db: Session = Depends(get_db)):
    time = payload.get("time", "")
    district = payload.get("field") or payload.get("region") or ""
    companion = payload.get("companion", "")
    concept = payload.get("concept", "")

    q = db.query(models.Place)
    if district:
        q = q.filter(models.Place.district == district)
    candidates = q.limit(100).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="후보 장소를 찾을 수 없습니다.")

    candidate_map = {p.id: p for p in candidates}
    candidate_text = _build_candidate_text(candidates)

    system = (
        "You MUST return JSON only. Given the user parameters and a list of candidates (id|title|category|addr|lat|lng), "
        "produce an object with keys: message, course. course must include title,totalTime,start(starts with name,lat,lng), "
        "and stops array where each item has id (integer from candidate list), description, stay (e.g. '20분'). "
        "Use only ids from the provided candidate list. Max 5 stops."
    )
    user = {
        "time": time,
        "district": district,
        "companion": companion,
        "concept": concept,
    }
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"INPUT: {json.dumps(user, ensure_ascii=False)}\nCandidates:\n{candidate_text}"},
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
        )
        model_text = resp.choices[0].message.content
    except Exception:
        logger.exception("OpenAI 호출 실패")
        raise HTTPException(status_code=500, detail="AI 서비스 호출 실패")

    parsed = _safe_parse_json(model_text)
    if not parsed:
        return {"type": "error", "message": "모델 응답 파싱 실패", "debug": {"model_raw": model_text}}

    stops_out = []
    invalid_ids = []
    for s in parsed.get("course", {}).get("stops", []):
        # support either {"id":...} or plain id entries
        try:
            pid_raw = s.get("id") if isinstance(s, dict) else s
            pid = int(pid_raw)
        except Exception:
            continue
        p = candidate_map.get(pid)
        if not p:
            invalid_ids.append(pid)
            continue
        description = s.get("description") if isinstance(s, dict) else (p.addr1 or "")
        stay = s.get("stay") if isinstance(s, dict) else ""
        stops_out.append({
            "id": pid,
            "name": p.title,
            "category": p.category,
            "description": description,
            "stay": stay,
            "lat": p.lat,
            "lng": p.lng,
        })

    course = parsed.get("course", {})
    course["stops"] = stops_out
    # 항상 고정 start 사용
    course["start"] = START_POINT

    message_text = parsed.get("message") or "요청하신 코스를 생성했습니다."
    debug = {"model_raw": model_text}
    if invalid_ids:
        debug["invalid_ids"] = invalid_ids

    return {"message": message_text, "course": course, "debug": debug}

@router.post("/api/course/modify")
def modify_course(payload: dict = Body(...), db: Session = Depends(get_db)):
    request_text = payload.get("request", "")
    course = payload.get("course", {})

    # derive district from current course if possible
    district = ""
    if course.get("stops"):
        first = course["stops"][0]
        try:
            first_id = int(first.get("id") if isinstance(first, dict) else first)
            p = db.query(models.Place).filter(models.Place.id == first_id).first()
            if p:
                district = p.district or ""
        except Exception:
            pass

    q = db.query(models.Place)
    if district:
        q = q.filter(models.Place.district == district)
    candidates = q.limit(200).all()
    candidate_map = {p.id: p for p in candidates}

    # Ensure IDs that are already in the current course are present in candidate_map
    input_ids = []
    for s in course.get("stops", []):
        try:
            pid_raw = s.get("id") if isinstance(s, dict) else s
            input_ids.append(int(pid_raw))
        except Exception:
            continue
    missing_input_ids = [i for i in set(input_ids) if i not in candidate_map]
    if missing_input_ids:
        rows = db.query(models.Place).filter(models.Place.id.in_(missing_input_ids)).all()
        for r in rows:
            candidate_map[r.id] = r

    # candidate text for prompt (include any added input rows)
    candidate_text = _build_candidate_text(list(candidate_map.values()))

    system = (
        "You MUST return JSON only. Return an object with keys: message and course. "
        "Given the user's modification request and the current course (with stops by id), "
        "and a list of candidate places (id|title|category|addr|lat|lng), return an updated course object using only ids from the candidate list or ids already in the current course. "
        "Do NOT invent new numeric ids. Keep title/start if unchanged. Ensure stops are returned in order and include 'stay' for each stop. "
        "Also include a short 'message' (Korean) describing what changed."
    )
    
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"REQUEST: {request_text}\nCURRENT_COURSE: {json.dumps(course, ensure_ascii=False)}\nCandidates:\n{candidate_text}"},
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
        )
        model_text = resp.choices[0].message.content
    except Exception:
        logger.exception("OpenAI 호출 실패")
        raise HTTPException(status_code=500, detail="AI 서비스 호출 실패")

    parsed = _safe_parse_json(model_text)
    if not parsed:
        return {"type": "error", "message": "모델 응답 파싱 실패", "debug": {"model_raw": model_text}}

    # If model returned ids that are not yet in candidate_map, try to load them from DB
    returned_ids = []
    for s in parsed.get("course", {}).get("stops", []):
        try:
            pid_raw = s.get("id") if isinstance(s, dict) else s
            returned_ids.append(int(pid_raw))
        except Exception:
            continue

    missing_returned_ids = [i for i in set(returned_ids) if i not in candidate_map]
    added_ids = []
    if missing_returned_ids:
        rows = db.query(models.Place).filter(models.Place.id.in_(missing_returned_ids)).all()
        for r in rows:
            candidate_map[r.id] = r
            added_ids.append(r.id)

    # Build output stops, skipping any ids that still aren't in DB
    new_stops = []
    invalid_ids = []
    for s in parsed.get("course", {}).get("stops", []):
        try:
            pid_raw = s.get("id") if isinstance(s, dict) else s
            pid = int(pid_raw)
        except Exception:
            continue
        p = candidate_map.get(pid)
        if not p:
            invalid_ids.append(pid)
            continue
        new_stops.append({
            "id": pid,
            "name": p.title,
            "category": p.category,
            "description": s.get("description") or (p.addr1 or ""),
            "stay": s.get("stay") or "",
            "lat": p.lat,
            "lng": p.lng,
        })

    course_out = parsed.get("course", {})
    # preserve start if model omitted it
    if not course_out.get("start"):
        if course.get("start"):
            course_out["start"] = course.get("start")
        elif new_stops:
            course_out["start"] = {
                "name": new_stops[0]["name"],
                "lat": new_stops[0]["lat"],
                "lng": new_stops[0]["lng"],
            }
    # 항상 고정 start 사용
    course_out["start"] = START_POINT

    message_text = parsed.get("message") or f"요청 '{request_text}'이(가) 반영된 코스입니다."
    debug = {"model_raw": model_text}
    if added_ids:
        debug["added_ids"] = added_ids
    if invalid_ids:
        debug["invalid_ids"] = invalid_ids

    return {"message": message_text, "course": course_out, "debug": debug}