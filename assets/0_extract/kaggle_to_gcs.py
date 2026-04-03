""" @bruin
name: suara_id.kaggle_to_gcs
type: python
connection: gcp-default
materialization:
  type: table
description: "Extracts the Indonesian Ethnic Speech dataset from Kaggle and loads it into the GCS Data Lake. Records the batch upload metadata."
owner: "ana@suara-id.com"
custom_checks:
  - name: "check_files_uploaded"
    description: "Ensure that at least one file was successfully moved to the Data Lake."
    query: "SELECT count(*) FROM suara_id.kaggle_to_gcs WHERE total_files_uploaded > 0"
    value: 1
columns:
  - name: batch_id
    type: string
    description: "Unique identifier for this ingestion batch."
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: total_files_uploaded
    type: int64
    description: "The count of .wav files successfully transferred to GCS."
    checks:
      - name: not_null
      - name: positive
  - name: source_dataset
    type: string
    description: "The Kaggle source path used for this extraction."
    checks:
      - name: not_null
@bruin """

import os
import shutil
import pandas as pd
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage

def materialize():
    dataset_name = "hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups"
    local_download_path = "/tmp/raw_audio"
    gcp_project = "suara-pipeline"
    bucket_name = "suara-lake-ananur"

    # 1. Kaggle Authentication
    api = KaggleApi()
    api.authenticate()
    
    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)
    
    # 2. Download
    print("Downloading from Kaggle...")
    api.dataset_download_files(dataset_name, path=local_download_path, unzip=True)

    # 3. GCS Connection
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)

    upload_count = 0
    for root, _, files in os.walk(local_download_path):
        for file in files:
            if file.endswith(".wav"):
                blob = bucket.blob(file) 
                blob.upload_from_filename(os.path.join(root, file))
                upload_count += 1
                if upload_count % 100 == 0:
                    print(f"Uploaded {upload_count} files...")

    # 4. Cleanup local storage
    shutil.rmtree(local_download_path)
    
    # 5. Return Metadata for Bruin Table
    print(f"Extraction complete. {upload_count} files in GCS.")
    return pd.DataFrame([{
        "batch_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total_files_uploaded": upload_count,
        "source_dataset": dataset_name
    }])