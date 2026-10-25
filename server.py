import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = {}

@app.get("/delta")
def get_delta_key(url: str):
    if not url or "auth.platorelay.com" not in url:
        return {"error": "Invalid Platorelay URL"}

    if url in cache:
        if time.time() - cache[url]['time'] < 3600:
            return {"key": cache[url]['key'], "cached": True, "times": "0s"}

    start_time = time.time()
    
    try:
        # We use a public, updated bypass API to do the heavy lifting
        api_url = f"https://delta-bypass-api.onrender.com/delta?url={url}"
        res = requests.get(api_url, timeout=45)
        data = res.json()
        
        if "key" in data:
            key = data["key"]
            cache[url] = {'key': key, 'time': time.time()}
            return {"key": key, "cached": False, "times": f"{round(time.time() - start_time, 1)}s"}
        else:
            return {"error": data.get("error", "Failed to solve via API")}
            
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

# --- SERVE THE WEBSITE ---
@app.get("/")
def serve_index():
    return FileResponse("index.html")
