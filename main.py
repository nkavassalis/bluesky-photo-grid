#!/usr/bin/env python3
import sys
import requests
import hashlib
import yaml
import json
from pathlib import Path
from urllib.parse import quote
from cdn import get_cdn
from jinja2 import Environment, FileSystemLoader


def validate_config(config):
    required_keys = {
        "bluesky": ["handle", "app_password"],
        "output": ["directory", "posts_per_chunk"],
        "website": ["title", "subtitle", "footer"],
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


def get_session(handle, password):
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    resp = requests.post(url, json={"identifier": handle, "password": password})
    resp.raise_for_status()
    data = resp.json()
    return data["accessJwt"], data["did"]


def fetch_all_posts(handle, jwt, limit=100):
    headers = {"Authorization": f"Bearer {jwt}"}
    cursor = None
    all_posts = []

    while True:
        url = f"https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed?actor={handle}&limit={limit}"
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

    return all_posts


def extract_images(posts, handle):
    images = []
    for item in posts:
        post = item.get("post", {})
        uri = post.get("uri")
        embed = post.get("embed", {})
        description = post.get("record", {}).get("text", "")
        created_at = post.get("record", {}).get("createdAt", "")[:10]
        if "images" in embed:
            for img in embed["images"]:
                src = img.get("fullsize") or img.get("thumb")
                if src and uri:
                    rkey = uri.split("/")[-1]
                    link = f"https://bsky.app/profile/{handle}/post/{rkey}"
                    images.append({"src": src, "link": link, "description": description, "date": created_at})
    return images


def save_images_json(images, output_dir, chunk_size):
    json_dir = output_dir / "data"
    json_dir.mkdir(parents=True, exist_ok=True)
    chunks = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]

    for idx, chunk in enumerate(chunks):
        json_file = json_dir / f"images_page_{idx + 1}.json"
        with open(json_file, "w") as f:
            json.dump(chunk, f, indent=2)


def render_template(output_dir, website_title, website_subtitle, website_footer):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template("index_template.html")
    html_output = template.render(
        WEBSITE_TITLE=website_title,
        WEBSITE_SUBTITLE=website_subtitle,
        WEBSITE_FOOTER=website_footer
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
    posts = fetch_all_posts(config["bluesky"]["handle"], jwt)
    images = extract_images(posts, config["bluesky"]["handle"])
    save_images_json(images, output_dir, config["output"]["posts_per_chunk"])
    render_template(output_dir, config["website"]["title"], config["website"]["subtitle"], config["website"]["footer"])
    copy_style_css(output_dir)
    sync_files(output_dir, hashes_file, config["cdn"], config)

