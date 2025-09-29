## Quick Start for GitHub Pages 

### 1. Clone repo and install requirements

```bash
git clone https://github.com/nkavassalis/bluesky-photo-grid.git

cd bluesky-photo-grid
pip install -r requirements.txt
```


### 2. Generate an App Password

Create a Bluesky app-specific password:

[Generate your App Password](https://bsky.app/settings/app-passwords)


### 3. Setup your GitHub Pages Repo

[Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)


### 4. Ensure your local git command is setup to access your GitHub account

[Setup the git CLI](https://docs.github.com/en/get-started/git-basics/set-up-git)

### 5. Fill out config.yaml

Include your bluesky app specific password, S3 bucket, and CF distribution ID. Update style.css as desired!

example:
```
bluesky:
  handle: "nkavassalis.bsky.social"
  app_password: "<REDACTED>"

output:
  directory: "output_site"
  posts_per_page: 25
  host_images: false

cdn:
  type: github_pages 

github:
  repo_path: "/home/nick/photog-site"
  repo_url: "git@github.com:nkavassalis/photog-site.git"

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


### 6. Run the app to create and upload the static website

Set your app password and run the script:

```bash
python3 main.py <config.yaml>
```


### 7. Schedule Regular Updates

Schedule automated updates with cron (daily, hourly, etc.):

* **Hourly**

```bash
0 * * * * python3 /full/path/to/main.py /full/path/to/config.yaml >/dev/null 2>&1
```

Adjust the cron frequency to suit your needs. It will only upload to the CDN if there are changes against the local content.


