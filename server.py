import time
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = {}

async def solve_with_browser(url: str):
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Go to the platorelay URL
            await page.goto(url, timeout=30000)
            
            # Wait for the key to appear on the page
            # Platorelay usually puts the key in a specific element or just text on the page
            # We will wait for the page to redirect or for text containing "FREE_" to appear
            await page.wait_for_selector("text=FREE_", timeout=25000)
            
            # Get the full page text
            content = await page.content()
            
            # Extract the key using regex
            import re
            match = re.search(r'(FREE_[a-fA-F0-9]{32})', content)
            if match:
                return {"key": match.group(1)}
            else:
                return {"error": "Could not find key on the page."}
                
        except Exception as e:
            return {"error": f"Browser failed: {str(e)}"}
        finally:
            await browser.close()

@app.get("/delta")
async def get_delta_key(url: str):
    if not url or "auth.platorelay.com" not in url:
        return {"error": "Invalid Platorelay URL"}

    if url in cache:
        if time.time() - cache[url]['time'] < 3600:
            return {"key": cache[url]['key'], "cached": True, "times": "0s"}

    start_time = time.time()
    
    # Run the browser solver
    result = await solve_with_browser(url)
    
    if "error" in result:
        return result
        
    key = result["key"]
    cache[url] = {'key': key, 'time': time.time()}
    return {"key": key, "cached": False, "times": f"{round(time.time() - start_time, 1)}s"}

# --- SERVE THE WEBSITE ---
@app.get("/")
def serve_index():
    return FileResponse("index.html")
