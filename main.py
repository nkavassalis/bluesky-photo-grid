#!/usr/bin/env python3
import sys
import requests
import hashlib
import yaml
import json
import datetime
from pathlib import Path
from urllib.parse import quote
from cdn import get_cdn
from jinja2 import Environment, FileSystemLoader
from xml.sax.saxutils import escape

def validate_config(config):
    required_keys = {
        "bluesky": ["handle", "app_password"],
        "output": ["directory", "posts_per_page"],
        "website": ["title", "subtitle", "footer", "base_url"],
        "cdn": ["type"]
    }

    missing_keys = []

    for section, keys in required_keys.items():
        if section not in config:
            missing_keys.append(section)
            continue

        for key in keys:
            if key not in config[section]:
                missing_keys.append(f"{section}.{key}")

    if missing_keys:
        raise KeyError("Missing required config keys: " + ", ".join(missing_keys))

    if "highres_tile" not in config["output"]:
        config["output"]["highres_tile"] = False

    if "host_images" not in config["output"]:
        config["output"]["host_images"] = False
 
    if "max_posts" not in config["bluesky"]:
        config["bluesky"]["max_posts"] = 1000

def get_session(handle, password):
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    resp = requests.post(url, json={"identifier": handle, "password": password})
    resp.raise_for_status()
    data = resp.json()
    return data["accessJwt"], data["did"]


def fetch_all_posts(handle, jwt, limit=100, max_posts=1000):
    headers = {"Authorization": f"Bearer {jwt}"}
    cursor = None
    all_posts = []

    while len(all_posts) < max_posts:
        remaining = max_posts - len(all_posts)
        current_limit = min(limit, remaining, 100)  # API max is 100 per call

        url = f"https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed?actor={handle}&limit={current_limit}"
        if cursor:
            url += f"&cursor={quote(cursor)}"

        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        feed = data.get("feed", [])
        if not feed:
            break

        true_posts = [
            item for item in feed
            if 'reason' not in item and 'reply' not in item.get('post', {}).get('record', {})
        ]

        all_posts.extend(true_posts)

        cursor = data.get("cursor")
        if not cursor:
            break

    return all_posts[:max_posts]


import time
import requests

def download_image(url, save_path, retries=3, backoff=5):
    if save_path.exists():
        return

    attempt = 0
    while attempt <= retries:
        try:
            resp = requests.get(url, stream=True, timeout=20)
            resp.raise_for_status()
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return  # success, exit function
        except (requests.RequestException, requests.Timeout) as e:
            attempt += 1
            if attempt > retries:
                print(f"[WARN] Failed to download {url} after {retries} retries: {e}")
                return  # skip, but don’t crash everything
            wait = backoff * attempt
            print(f"[INFO] Error fetching {url} ({e}), retrying in {wait}s...")
            time.sleep(wait)


def extract_images(posts, handle, output_dir, host_images=False):
    images = []
    for item in posts:
        post = item.get("post", {})
        uri = post.get("uri")
        embed = post.get("embed", {})
        description = post.get("record", {}).get("text", "")
        created_at = post.get("record", {}).get("createdAt", "")[:10]
        if "images" in embed:
            for img in embed["images"]:
                src = img.get("fullsize")
                thumb = img.get("thumb") 
                if src and uri:
                    rkey = uri.split("/")[-1]
                    link = f"https://bsky.app/profile/{handle}/post/{rkey}"

                    if host_images:
                        img_path = output_dir / "hosted_images"
                        src_filename = img_path / f"{rkey}_full.jpg"
                        thumb_filename = img_path / f"{rkey}_thumb.jpg"
                        download_image(src, src_filename)
                        download_image(thumb, thumb_filename)
                        src = str(src_filename.relative_to(output_dir))
                        thumb = str(thumb_filename.relative_to(output_dir))

                    images.append({
                        "id": rkey, 
                        "src": src, 
                        "thumb": thumb, 
                        "link": link, 
                        "description": description, 
                        "date": created_at
                    })
    return images


def save_images_json(images, output_dir):
    json_dir = output_dir / "data"
    json_dir.mkdir(parents=True, exist_ok=True)

    json_file = json_dir / "images.json"
    with open(json_file, "w") as f:
        json.dump(images, f, indent=2)


def render_template(output_dir, config):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template("index_template.html")
    html_output = template.render(
        WEBSITE_TITLE=config["website"]["title"],
        WEBSITE_SUBTITLE=config["website"]["subtitle"],
        WEBSITE_FOOTER=config["website"]["footer"],
        config=config
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html_output, encoding="utf-8")


def copy_style_css(output_dir):
    src_css = Path(__file__).parent / "style.css"
    dst_css = output_dir / "style.css"
    dst_css.write_text(src_css.read_text(encoding="utf-8"), encoding="utf-8")


def compute_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_hashes(hashes_file):
    return json.loads(hashes_file.read_text()) if hashes_file.exists() else {}


def save_hashes(hashes, hashes_file):
    hashes_file.write_text(json.dumps(hashes, indent=2))

def generate_rss_feed(images, output_dir, config, feed_size=25):
    rss_items = []
    feed_images = images[:feed_size]
    base_url = config["website"].get("base_url")
    feed_url = f"{base_url}/feed.xml"

    for img in feed_images:
        guid_url = img['link']
        description_text = escape(img['description'])

        rss_items.append(f"""
        <item>
            <title>{description_text[:50]}</title>
            <link>{base_url}/img-{{img['rkey']}</link>
            <description>{description_text}</description>
            <pubDate>{datetime.datetime.strptime(img['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 GMT')}</pubDate>
            <guid>{img['rkey']}</guid>
        </item>""")

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(config["website"]["title"])}</title>
    <link>{base_url}</link>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml" />
    <description>{escape(config["website"]["title"])} RSS feed</description>
    {''.join(rss_items)}
  </channel>
</rss>"""

    (output_dir / "feed.xml").write_text(rss_feed, encoding="utf-8")

def sync_files(output_dir, hashes_file, cdn_config, config):
    cdn = get_cdn(cdn_config["type"], config)
    prev_hashes = load_hashes(hashes_file)
    current_hashes = {}

    files_to_upload = []
    for file in output_dir.rglob("*"):
        if file.is_file() and file.name != hashes_file.name:
            file_hash = compute_hash(file)
            relative = file.relative_to(output_dir).as_posix()
            current_hashes[relative] = file_hash

            if prev_hashes.get(relative) != file_hash:
                files_to_upload.append(relative)

    if files_to_upload:
        cdn.upload_files(files_to_upload, output_dir)

    save_hashes(current_hashes, hashes_file)

if __name__ == "__main__":
    try:
        config_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        config = yaml.safe_load(config_file.read_text())
        validate_config(config)

        output_dir = Path(config["output"]["directory"])
        hashes_file = output_dir / ".file_hashes.json"

    except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
        print(f"Config Error: {e}")
        sys.exit(1)

    jwt, _ = get_session(config["bluesky"]["handle"], config["bluesky"]["app_password"])
    posts = fetch_all_posts(config["bluesky"]["handle"], jwt, config["bluesky"]["max_posts"])
    images = extract_images(posts, config["bluesky"]["handle"], output_dir, config["output"]["host_images"])
    save_images_json(images, output_dir)
    render_template(output_dir, config)
    copy_style_css(output_dir)
    generate_rss_feed(images, output_dir, config)  
    sync_files(output_dir, hashes_file, config["cdn"], config)

