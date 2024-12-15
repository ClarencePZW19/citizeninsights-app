# list datasets into portal and select from the list
from google.cloud import storage
import pandas as pd
import io
import json

client = storage.Client(project='winged-keyword-441104-q1')

def list_blobs(bucket_name):
    bucket_name = bucket_name

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        print(blob.name)


def download_blob():
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    bucket_name = "citizeninsghit"
    source_blob_name = "datasetlist/data.gov.sg datasets log - target datasets.csv"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    contents = blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(contents))
    data = df.to_dict(orient='records')
    # json_data = json.dumps(data, indent=4)
    # print(json_data[0])
    return data




