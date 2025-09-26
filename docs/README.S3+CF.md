## Quick Start for S3 + CloudFront (for SSL)

### 1. Clone repo and install requirements

```bash
git clone https://github.com/nkavassalis/bluesky-photo-grid.git

cd bluesky-photo-grid
pip install -r requirements.txt
```


### 2. Generate an App Password

Create a Bluesky app-specific password:

[Generate your App Password](https://bsky.app/settings/app-passwords)


### 3. Setup your S3 website bucket and Cloudfront distribution with SSL for your domain

[Setup an S3 static website](https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html)

[Use an Amazon CloudFront distribution to serve a static website](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started-cloudfront-overview.html)


### 4. Install the AWS CLI

[Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

Make sure to run

```bash
aws configure
```

[and setup the credentials for your account.](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)


### 5. Fill out config.yaml

Include your bluesky app specific password, S3 bucket, and CF distribution ID. Update style.css as desired!

example:
```
bluesky:
  handle: "nkavassalis.bsky.social"
  app_password: "<REDACTED>"

output:
  directory: "output_site"
  posts_per_chunk: 25
  host_images: false

cdn:
  type: s3_cloudfront

aws:
  s3_bucket: "photog.jp"
  cloudfront_dist_id: "E2X6WM52ECH4WR"

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


