import subprocess
from .base import CDN

class S3CDN(CDN):
    def upload_files(self, files_to_upload, output_dir):
        bucket = self.config["aws"]["s3_bucket"]

        cmd = [
            "aws", "s3", "sync",
            str(output_dir),
            f"s3://{bucket}/",
            "--acl", "public-read",
            "--exclude", "*",
            "--no-progress",
            "--only-show-errors"
        ]

        for file_path in files_to_upload:
            cmd.extend(["--include", file_path])

        subprocess.run(cmd, check=True)

        print(f"Uploaded {len(files_to_upload)} files to S3 bucket: {bucket}.")
