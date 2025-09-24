import subprocess
from .base import CDN

class S3CDN(CDN):
    def upload_files(self, files_to_upload, output_dir):
        bucket = self.config["aws"]["s3_bucket"]

        for rel_path in files_to_upload:
            subprocess.run([
                "aws", "s3", "cp",
                str(output_dir / rel_path),
                f"s3://{bucket}/{rel_path}",
                "--acl", "public-read"
            ], check=True)

        print(f"Uploaded {len(files_to_upload)} files to S3 bucket: {bucket}.")

