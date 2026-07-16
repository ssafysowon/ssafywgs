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

import math, re
import copy

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

def _strip_ids_from_message(msg: str):
    if not msg:
        return msg
    # 괄호 안의 순수 숫자 패턴 제거: "석촌호수(7)" → "석촌호수"
    out = re.sub(r'\(\s*\d+\s*\)', '', msg)
    out = re.sub(r'\s{2,}', ' ', out).strip()
    return out

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
    course["start"] = START_POINT

    # validate/adjust based on requested time
    adjust_msg = None
    time_limit = parse_time_to_minutes(time)
    if time_limit:
        course, adjust_msg = validate_and_adjust_course(course, time_limit, start_point=START_POINT)
        final_total = compute_total_minutes(course, course.get("start", START_POINT))
        course["totalTime"] = minutes_to_text(final_total)

    message_text = _strip_ids_from_message(parsed.get("message", "") or "")
    if not message_text:
        message_text = "요청하신 코스를 생성했습니다."
    if adjust_msg:
        message_text = f"{message_text} ({adjust_msg})"
    logger.debug("AI raw response: %s", model_text)

    return {"message": message_text, "course": course}

@router.post("/api/course/modify")
def modify_course(payload: dict = Body(...), db: Session = Depends(get_db)):
    request_text = payload.get("request", "")
    time = payload.get("time", "")            # <-- 추가: 클라이언트가 보낸 제한 시간
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
    course_out["stops"] = new_stops
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

    # validate/adjust using provided time (if any)
    adjust_msg = None
    time_limit = parse_time_to_minutes(time)
    if time_limit:
        course_out, adjust_msg = validate_and_adjust_course(course_out, time_limit, start_point=START_POINT)
        final_total = compute_total_minutes(course_out, course_out.get("start", START_POINT))
        course_out["totalTime"] = minutes_to_text(final_total)

    message_text = _strip_ids_from_message(parsed.get("message", "") or "")
    if not message_text:
        message_text = f"요청 '{request_text}'이(가) 반영된 코스입니다."
    if adjust_msg:
        message_text = f"{message_text} ({adjust_msg})"
    logger.debug("AI raw response: %s", model_text)

    return {"message": message_text, "course": course_out}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# 보행 전제: 직선 거리 보정 + 버퍼 추가
def estimate_travel_minutes(a_lat, a_lng, b_lat, b_lng, speed_kmh=4.5):
    straight_km = haversine_km(a_lat, a_lng, b_lat, b_lng)

    # 실제 보행 경로는 직선보다 길어짐
    estimated_route_km = straight_km * 1.3

    travel_minutes = estimated_route_km / speed_kmh * 60

    # 신호 대기, 길 찾기 여유
    travel_minutes += 2

    return max(1, int(round(travel_minutes)))

def parse_stay_minutes(stay_text, default=30):
    if not stay_text:
        return default
    m = re.search(r'(?:(\d+)\s*시간)?\s*(\d+)?\s*분?', stay_text)
    if not m:
        m2 = re.search(r'(\d+)', stay_text)
        return int(m2.group(1)) if m2 else default
    hours = int(m.group(1)) if m.group(1) else 0
    mins = int(m.group(2)) if m.group(2) else 0
    return hours*60 + mins if (hours or mins) else default

def compute_total_minutes(course, start_point, speed_kmh=4.5, default_stay=30):
    total = 0
    prev_lat, prev_lng = start_point['lat'], start_point['lng']
    for s in course.get('stops', []):
        travel = estimate_travel_minutes(prev_lat, prev_lng, s['lat'], s['lng'], speed_kmh)
        stay = parse_stay_minutes(s.get('stay', ''), default=default_stay)
        total += travel + stay
        prev_lat, prev_lng = s['lat'], s['lng']
    return total

# 시간 문자열을 분으로 변환
def parse_time_to_minutes(time_str):
    if not time_str:
        return None
    if isinstance(time_str, (int, float)):
        return int(time_str)
    s = str(time_str)
    h_m = re.search(r'(\d+)\s*시간', s)
    m_m = re.search(r'(\d+)\s*분', s)
    hours = int(h_m.group(1)) if h_m else 0
    mins = int(m_m.group(1)) if m_m else 0
    if h_m or m_m:
        return hours * 60 + mins
    digits = re.search(r'^\s*(\d+)\s*$', s)
    if digits:
        return int(digits.group(1))
    return None

def minutes_to_text(minutes):
    minutes = int(minutes)
    if minutes >= 60:
        h = minutes // 60
        m = minutes % 60
        return f"{h}시간 {m}분" if m else f"{h}시간"
    return f"{minutes}분"

# course 검증·보정 함수 (체류시간 축소 → 그래도 초과면 마지막 정류장부터 제거)
def validate_and_adjust_course(course_in, time_limit_minutes, start_point=START_POINT, speed_kmh=4.5, default_stay=30, min_stay=10):
    if not time_limit_minutes:
        return course_in, None
    course = copy.deepcopy(course_in)
    if not course.get("start"):
        course["start"] = start_point
    stops = course.get("stops", []) or []
    stays = [parse_stay_minutes(s.get("stay", ""), default=default_stay) for s in stops]

    removed = []
    reduced_any = False

    while True:
        total = compute_total_minutes(course, course["start"], speed_kmh=speed_kmh, default_stay=default_stay)
        if total <= time_limit_minutes:
            break

        excess = total - time_limit_minutes
        reducible = [max(0, m - min_stay) for m in stays]
        sum_reducible = sum(reducible)

        if sum_reducible > 0:
            # 비례로 줄이되 min_stay 이상으로 유지
            for i, r in enumerate(reducible):
                if r <= 0:
                    continue
                alloc = min(r, int(math.ceil(excess * (r / sum_reducible))))
                stays[i] -= alloc
                excess -= alloc
                if excess <= 0:
                    break
            # 남은 초과는 뒤에서 채우기
            i = len(stays) - 1
            while excess > 0 and i >= 0:
                can = stays[i] - min_stay
                if can > 0:
                    take = min(can, excess)
                    stays[i] -= take
                    excess -= take
                i -= 1
            # 문자열로 반영
            for idx, s in enumerate(stops):
                s["stay"] = minutes_to_text(stays[idx])
            reduced_any = True
            continue

        # 더 줄일 수 없다면 마지막 정류장 제거
        if stops:
            last = stops.pop()
            removed.append(last.get("name") or last.get("id"))
            stays.pop()
            course["stops"] = stops
            continue

        # 정류장 모두 제거해도 안되면 중단
        break

    final_total = compute_total_minutes(course, course["start"], speed_kmh=speed_kmh, default_stay=default_stay)
    notes = []
    if reduced_any:
        notes.append("체류시간을 단축했습니다.")
    if removed:
        notes.append(f"마지막 장소 {len(removed)}곳을 제거했습니다.")
    notes.append(f"총 소요시간: {minutes_to_text(final_total)}")
    if final_total > time_limit_minutes:
        notes.append(f"제한시간({minutes_to_text(time_limit_minutes)})을 맞출 수 없습니다.")
    return course, " ".join(notes)