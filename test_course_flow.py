import urllib.request
import json
import sys

BASE = "http://localhost:8000"

def post_json(path, payload, timeout=30):
    url = BASE + path
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

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
    gen_resp = post_json("/api/course/generate", gen_payload)
    pretty_print("OUTPUT (generate):", gen_resp)

    original_course = gen_resp.get("course")
    if not original_course:
        print("서버가 `course`를 반환하지 않았습니다.")
        sys.exit(1)

    modify_payload = {
        "request": "카페 하나 더 넣어줘",
        "course": original_course
    }

    print("\n=== MODIFY ===")
    pretty_print("INPUT (modify):", modify_payload)
    mod_resp = post_json("/api/course/modify", modify_payload)
    pretty_print("OUTPUT (modify):", mod_resp)

if __name__ == "__main__":
    main()