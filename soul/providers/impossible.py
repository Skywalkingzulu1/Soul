import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from soul.core.logger import setup_logger

logger = setup_logger(__name__)


class ImpossibleCloudClient:
    """Native S3 client for Impossible Cloud."""

    def __init__(
        self, endpoint: str = None, access_key: str = None, secret_key: str = None
    ):
        """Initialize with optional overrides."""
        # Lazy import to avoid circular dependency
        from soul.core.config import config

        self.endpoint = endpoint or config.impossible_cloud_endpoint
        self.access_key = access_key or config.impossible_cloud_access_key
        self.secret_key = secret_key or config.impossible_cloud_secret_key
        self.connected = False
        self.s3 = None

        # Validate credentials before creating client
        if not self.endpoint:
            logger.error("Impossible Cloud endpoint not configured")
            return

        if not self.access_key or not self.secret_key:
            logger.warning("Impossible Cloud credentials not configured")
            return

        # Create S3 client
        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
        )

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test the S3 connection and log result."""
        try:
            self.s3.list_buckets()
            self.connected = True
            logger.info(f"Successfully connected to Impossible Cloud: {self.endpoint}")
        except EndpointConnectionError as e:
            logger.error(
                f"Cannot connect to Impossible Cloud endpoint: {self.endpoint}"
            )
            logger.error(f"Error: {e}")
            self.connected = False
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"Impossible Cloud authentication failed: {error_code}")
            logger.error(f"Error: {e}")
            self.connected = False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Impossible Cloud: {e}")
            self.connected = False

    def is_available(self) -> bool:
        """Check if client is connected."""
        return self.connected and self.s3 is not None

    def list_buckets(self):
        """List all buckets in the account."""
        if not self.is_available():
            logger.warning("Cannot list buckets: client not connected")
            return []

        try:
            response = self.s3.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
            logger.info(f"Found {len(buckets)} buckets")
            return buckets
        except Exception as e:
            logger.error(f"Failed to list buckets: {e}")
            return []

    def upload_file(self, file_path, bucket, object_name=None) -> bool:
        """Upload a file to an S3 bucket."""
        if not self.is_available():
            logger.error("Cannot upload: client not connected")
            return False

        if object_name is None:
            import os

            object_name = os.path.basename(file_path)

        try:
            self.s3.upload_file(file_path, bucket, object_name)
            logger.info(f"Successfully uploaded {file_path} to {bucket}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def download_file(self, bucket, object_name, file_path) -> bool:
        """Download a file from an S3 bucket."""
        if not self.is_available():
            logger.error("Cannot download: client not connected")
            return False

        try:
            self.s3.download_file(bucket, object_name, file_path)
            logger.info(
                f"Successfully downloaded {bucket}/{object_name} to {file_path}"
            )
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

    def list_objects(self, bucket, prefix: str = "") -> list:
        """List objects in a bucket with optional prefix."""
        if not self.is_available():
            return []

        try:
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            return []
        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            return []
