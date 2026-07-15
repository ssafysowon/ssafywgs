import urllib.request
import json
import re
import sys

BASE = "http://localhost:8000"


def post_json(path, payload, timeout=30):
    url = BASE + path
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def safe_parse_json(text):
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


def pretty_print(title, obj):
    print(title)
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main():
    gen_payload = {
        "time": "1시간",
        "field": "강남구",
        "companion": "싸피 친구와",
        "concept": "조용히 걷기 좋은"
    }

    print("=== GENERATE ===")
    pretty_print("INPUT (generate):", gen_payload)
    try:
        gen_resp = post_json("/api/course/generate", gen_payload)
    except Exception as e:
        print("Generate 요청 실패:", e)
        sys.exit(1)
    pretty_print("OUTPUT (generate):", gen_resp)

    model_raw = gen_resp.get("debug", {}).get("model_raw")
    if not model_raw:
        print("debug.model_raw가 없습니다. 모델 원본 응답이 필요합니다.")
        sys.exit(1)

    parsed = safe_parse_json(model_raw)
    if not parsed or not parsed.get("course"):
        print("model_raw에서 course 파싱 실패")
        print("model_raw:", model_raw)
        sys.exit(1)

    # prefer server-processed course (has START_POINT and enriched names)
    original_course = gen_resp.get("course")
    if not original_course:
        model_raw = gen_resp.get("debug", {}).get("model_raw")
        if not model_raw:
            print("debug.model_raw가 없습니다. 모델 원본 응답이 필요합니다.")
            sys.exit(1)
        parsed = safe_parse_json(model_raw)
        if not parsed or not parsed.get("course"):
            print("model_raw에서 course 파싱 실패")
            print("model_raw:", model_raw)
            sys.exit(1)
        original_course = parsed["course"]

    modify_payload = {
        "request": "카페 하나 더 넣어줘",
        "course": original_course
    }

    print("\n=== MODIFY ===")
    pretty_print("INPUT (modify):", modify_payload)
    try:
        mod_resp = post_json("/api/course/modify", modify_payload)
    except Exception as e:
        print("Modify 요청 실패:", e)
        sys.exit(1)
    pretty_print("OUTPUT (modify):", mod_resp)


if __name__ == "__main__":
    main()