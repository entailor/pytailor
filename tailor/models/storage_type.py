from enum import Enum


class StorageType(str, Enum):
    AZURE_BLOB_CONTAINER = "AZURE_BLOB_CONTAINER"
    LOCAL_FILESYSTEM = "LOCAL_FILESYSTEM"
    S3_BUCKET = "S3_BUCKET"
