import subprocess
import shutil
from pathlib import Path
from .base import CDN

class GitHubPagesCDN(CDN):
    def upload_files(self, files_to_upload, output_dir):
        gh_pages_dir = Path(self.config["github"]["repo_path"])
        gh_pages_dir.mkdir(parents=True, exist_ok=True)

        if not (gh_pages_dir / ".git").exists():
            subprocess.run(["git", "init"], cwd=gh_pages_dir, check=True)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=gh_pages_dir, check=True)
            subprocess.run(["git", "remote", "add", "origin", self.config["github"]["repo_url"]], cwd=gh_pages_dir, check=True)

        for rel_path in files_to_upload:
            src = output_dir / rel_path
            dst = gh_pages_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        subprocess.run(["git", "add", "."], cwd=gh_pages_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Update GitHub Pages"], cwd=gh_pages_dir, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=gh_pages_dir, check=True)

        print(f"Uploaded {len(files_to_upload)} files to GitHub Pages ({gh_pages_dir}).")

