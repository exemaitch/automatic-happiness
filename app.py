from aws_cdk import aws_s3, core


class S3Bucket(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)
        bucket = aws_s3.Bucket(self, "MyTestBucket")

app = core.App()
S3Bucket(app, "S3BucketTest")
app.synth()
