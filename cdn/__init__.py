from .local import LocalCDN
from .s3 import S3CDN
from .s3_cloudfront import S3CloudFrontCDN
from .github_pages import GitHubPagesCDN

def get_cdn(cdn_type, config):
    if cdn_type == "local":
        return LocalCDN(config)
    elif cdn_type == "s3":
        return S3CDN(config)
    elif cdn_type == "s3_cloudfront":
        return S3CloudFrontCDN(config)
    elif cdn_type == "github_pages":
        return GitHubPagesCDN(config)
    else:
        raise ValueError(f"Unsupported CDN type: {cdn_type}")

