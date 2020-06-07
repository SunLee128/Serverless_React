import json
import boto3
from botocore.client import Config
import io
import zipfile
import mimetypes


def lambda_handler(event, context):

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:730163571022:deployPorfolio')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.sunlee.info')
        build_bucket = s3.Bucket('portfoliobuild.sunlee.info')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(
                    obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject="Portfolio has been deployed succesfully!",
                      Message="Portfolio has been deployed succesfully!")
        print("Hello from deployPortfolio")
    except:
        topic.publish(Subject="Portfolio deploy failed",
                      Message="Portfolio deploy failed")
        raise
    return "Hello from Lambda"
