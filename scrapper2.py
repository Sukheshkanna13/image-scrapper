import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from base64 import b64decode
from datetime import datetime

# --- Helper Function to Choose Best URL from a srcset ---
def choose_best_srcset(srcset):
    """
    Given a srcset string (multiple comma separated URLs with resolutions),
    choose and return the URL with the highest multiplier.
    """
    candidates = []
    for item in srcset.split(","):
        parts = item.strip().split(" ")
        url = parts[0]
        multiplier = 1.0
        if len(parts) > 1:
            try:
                multiplier = float(parts[1].rstrip("x"))
            except Exception:
                multiplier = 1.0
        candidates.append((multiplier, url))
    if candidates:
        best_url = sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]
        return best_url
    return None

# --- STEP 1: (Optional) Fetch HTML using Zyte API ---
# Uncomment the following block if you wish to fetch the HTML on the fly.
"""
zyte_api_key = "kannassukesh"  # Your Zyte API key
product_url = "https://www.instacart.com/products/18684158-progresso-traditional-creamy-chicken-noodle-soup-18-500-oz?retailerSlug=foodsco"

api_response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth=(zyte_api_key, ""),
    json={
        "url": product_url,
        "httpResponseBody": True,
    },
)

response_json = api_response.json()
if "httpResponseBody" not in response_json:
    raise KeyError("The key 'httpResponseBody' was not found in the API response. Full response:\n" + str(response_json))

html_bytes = b64decode(response_json["httpResponseBody"])
html_content = html_bytes.decode("utf-8")
"""

# --- STEP 2: Read HTML Content from a Local File ---
html_file = "http_response_body.html"
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# --- STEP 3: Create a New Output Directory Based on Timestamp ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = f"downloaded_images_{timestamp}"
os.makedirs(output_folder, exist_ok=True)
print(f"Images will be saved to: {output_folder}")

# --- STEP 4: Parse HTML and Extract Image URLs ---
soup = BeautifulSoup(html_content, "html.parser")
base_url = "https://www.instacart.com/"  # Adjust base URL as needed

image_urls = set()

# (a) From <img> tags
for img in soup.find_all("img"):
    # Check multiple attributes
    for attr in ["src", "data-src", "srcset"]:
        url = img.get(attr)
        if url:
            if attr == "srcset":
                best = choose_best_srcset(url)
                if best:
                    image_urls.add(best)
            else:
                image_urls.add(url)

# (b) From <source> tags (often inside <picture>)
for source in soup.find_all("source"):
    for attr in ["src", "srcset"]:
        url = source.get(attr)
        if url:
            if attr == "srcset":
                best = choose_best_srcset(url)
                if best:
                    image_urls.add(best)
            else:
                image_urls.add(url)

# (c) From <a> tags whose href looks like an image URL
img_exts = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
for a in soup.find_all("a"):
    href = a.get("href")
    if href and href.lower().endswith(img_exts):
        image_urls.add(href)

# (d) From inline styles with background images
bg_img_pattern = re.compile(r'background(?:-image)?\s*:\s*url\(["\']?(.*?)["\']?\)', re.IGNORECASE)
for tag in soup.find_all(True):
    style = tag.get("style")
    if style:
        matches = bg_img_pattern.findall(style)
        for match in matches:
            if match:
                image_urls.add(match)

print(f"Found {len(image_urls)} candidate image URLs.")

# --- STEP 5: Download the Images ---
for i, url in enumerate(image_urls):
    # Ensure the URL is absolute
    if not url.startswith("http"):
        img_url = urljoin(base_url, url)
    else:
        img_url = url

    print(f"[{i}] Downloading: {img_url}")
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        # Attempt to get the file extension; default to .jpg if missing or not common
        ext = os.path.splitext(img_url)[1]
        if not ext or ext.lower() not in img_exts:
            ext = ".jpg"
        filename = os.path.join(output_folder, f"image_{i}{ext}")
        with open(filename, "wb") as img_file:
            img_file.write(response.content)
        print(f"Saved image to {filename}")
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

