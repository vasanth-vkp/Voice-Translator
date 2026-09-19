import urllib.request
import json

print("=== 1. Testing GET /api/languages ===")
res = urllib.request.urlopen("http://127.0.0.1:8000/api/languages")
langs = json.loads(res.read())
print(f"Supported languages: {len(langs['languages'])} languages found.")
print("Popular samples:", langs['popular'][:6])

print("\n=== 2. Testing POST /api/translate ===")
payload = {
    "text": "Could you please tell me how to get to the modern art museum from here?",
    "source": "auto",
    "target": "es"
}
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/translate",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = urllib.request.urlopen(req)
data = json.loads(res.read())
print("Source Text   :", data["original_text"])
print("Detected Lang :", data["detected_lang"], f"({data['source_name']})")
print("Target Lang   :", data["target_lang"], f"({data['target_name']})")
print("Translation   :", data["translated_text"])

print("\n=== 3. Testing POST /api/speak ===")
speak_payload = {
    "text": data["translated_text"],
    "lang": "es"
}
req_speak = urllib.request.Request(
    "http://127.0.0.1:8000/api/speak",
    data=json.dumps(speak_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res_speak = urllib.request.urlopen(req_speak)
audio_bytes = res_speak.read()
print(f"Synthesized MP3 bytes received: {len(audio_bytes)} bytes")
print("Content-Type:", res_speak.headers.get("Content-Type"))

print("\n=== 4. Testing Static Frontend (GET /) ===")
res_web = urllib.request.urlopen("http://127.0.0.1:8000/")
html = res_web.read().decode("utf-8")
print(f"HTML response length: {len(html)} bytes, Status Code: {res_web.status}")
assert "VoiceBridge" in html
assert "view-translator" in html
assert "view-history" in html
assert "view-settings" in html
assert "view-mic-error" in html
print("Frontend assertions passed! Static mount is working perfectly.")

print("\n=== 5. Testing Static Assets (/logo.svg, /app.js) ===")
res_logo = urllib.request.urlopen("http://127.0.0.1:8000/logo.svg")
print(f"/logo.svg: {len(res_logo.read())} bytes, Status: {res_logo.status}")
res_js = urllib.request.urlopen("http://127.0.0.1:8000/app.js")
print(f"/app.js: {len(res_js.read())} bytes, Status: {res_js.status}")

print("\nALL BACKEND & FRONTEND TESTS PASSED SUCCESSFULLY!")
