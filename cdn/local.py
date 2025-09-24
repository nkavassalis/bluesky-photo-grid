import shutil
from pathlib import Path
from .base import CDN

class LocalCDN(CDN):
    def upload_files(self, files_to_upload, output_dir):
        destination = Path(self.config["local"]["directory"])
        destination.mkdir(parents=True, exist_ok=True)

        for rel_path in files_to_upload:
            src = output_dir / rel_path
            dst = destination / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        print(f"Copied {len(files_to_upload)} files to local directory: {destination}")

