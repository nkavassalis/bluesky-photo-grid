import subprocess
from .base import CDN

class S3CDN(CDN):
    def upload_files(self, files_to_upload, output_dir):
        bucket = self.config["aws"]["s3_bucket"]

        include_file = output_dir / ".s3_include_paths.txt"
        include_file.write_text("\n".join(files_to_upload))

        subprocess.run([
            "aws", "s3", "sync",
            str(output_dir),
            f"s3://{bucket}/",
            "--acl", "public-read",
            "--exclude", "*",
            "--include-from", str(include_file),
            "--no-progress",
            "--delete",
            "--only-show-errors",
        ], check=True)

        include_file.unlink(missing_ok=True)

        print(f"Uploaded {len(files_to_upload)} files to S3 bucket: {bucket}.")

