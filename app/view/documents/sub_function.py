import boto3
from botocore.config import Config

from app.config import S3Config

my_config = Config(
    signature_version='v4',
)

s3 = boto3.client(
    's3',
    config=my_config,
    region_name=S3Config.REGION,
    aws_access_key_id=S3Config.AWS_ACCESS,
    aws_secret_access_key=S3Config.AWS_SECRET,

)


def create_pre_signed_url(object_name):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': S3Config.BUCKET_NAME,
            'Key': object_name,
            'ResponseContentType': "application/pdf"
        },
        ExpiresIn=3600
    )
