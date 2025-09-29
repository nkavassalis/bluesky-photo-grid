# Bluesky Photo Grid 

Create a static website photo gallery from a Bluesky account using S3 (and optionally CloudFront), GitHub Pages, or any CDN you can rsync from a local directory to. Cron it to run as often as you want (it wont actually update files unless your Bluesky changes) and customize the look and feel as desired!

Uses [LightGallery](https://github.com/sachinchoolur/lightGallery) for the UI.

---

## Documentation

[Generic Quickstart](docs/README.local.md)

[AWS S3 Quickstart](docs/README.S3.md)

[AWS S3 + CloudFront Quickstart](docs/README.S3+CF.md)

[GitHub Pages Quickstart](docs/README.Github.md)

---

## Configuration 

```bash
bluesky:
  handle: <Your Bluesky handle>
  app_password: <The app password you generate, see docs>
  max_posts: <Performance, general crawl size, defaults to 1000 latest posts.>

output:
  directory: <the directory to store the locally build site>
  posts_per_page: <posts per page, consider performance / load time>
  host_images: <do you want to store the images in your cdn or refer to bluesky: true/false>
  highres_tiles: <do you want to use the full res images in the tile grid, consider performance: true/false>

cdn:
  type: <see docs>

website:
  title: <website title> 
  subtitle: |
         <html under the title, links, etc. update template to customize further>
  footer: |
         <html under the page. update template to customize further>
  base_url: <website this will appear on, for RSS feed>
```

---

## Live Demo

Check out a live demo here:

[photog.jp](https://photog.jp/)

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. I would love code for other CDNs. Should this support sources beyond Bluesky?

---

## LICENSE

GPL v3, see included LICENSE file

---
