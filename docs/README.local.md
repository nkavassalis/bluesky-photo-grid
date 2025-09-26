## Quick Start for generic websites

### 1. Clone repo and install requirements

```bash
git clone https://github.com/nkavassalis/bluesky-photo-grid.git

cd bluesky-photo-grid
pip install -r requirements.txt
```


### 2. Generate an App Password

Create a Bluesky app-specific password:

[Generate your App Password](https://bsky.app/settings/app-passwords)


[and setup the credentials for your account.](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)


### 3. Fill out config.yaml

Include your bluesky app specific password, S3 bucket, and CF distribution ID. Update style.css as desired!

example:
```
bluesky:
  handle: "nkavassalis.bsky.social"
  app_password: "<REDACTED>"

output:
  directory: "output_site"
  host_images: false
  posts_per_chunk: 25

cdn:
  type: local 

local:
  directory: "/home/nick/my-website-directory"

website:
  title: "photog nkavassalis"
  subtitle: |
    <a href='https://root.wtf'>bio</a>
    <a href='https://baka.jp'>blog</a>
    <a href='https://bsky.app/profile/nkavassalis.bsky.social'>social</a>
    <a href='mailto:nick@baka.jp'>email</a>
  footer: |
    (c) Nick Kavassalis <script>document.write(new Date().getFullYear())</script>
  base_url: https://photog.jp
```


### 4. Run the app to create and upload the static website

Set your app password and run the script:

```bash
python3 main.py <config.yaml>
```

### 5. Schedule Regular Updates

Schedule automated updates with cron (daily, hourly, etc.):

* **Hourly**

```bash
0 * * * * python3 /full/path/to/main.py /full/path/to/config.yaml >/dev/null 2>&1
```

Adjust the cron frequency to suit your needs. It will only produce new files if there are changes to the local content.
