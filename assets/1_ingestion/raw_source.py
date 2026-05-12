""" @bruin
name: suara_id.raw_source
type: python
connection: gcp-default
materialization:
  type: table
depends:
  - suara_id.kaggle_to_gcs
description: "Ingests the list of available .wav files from the GCS Data Lake into BigQuery."
owner: "ana@suara-id.com"
custom_checks:
  - name: "check_only_wav_files"
    description: "Ensure that only .wav audio files are ingested."
    query: "SELECT count(*) FROM suara_id.raw_source WHERE audio_file_name NOT LIKE '%.wav'"
    value: 0
columns:
  - name: id
    type: int64
    description: "Unique integer identifier for each audio record."
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: audio_file_name
    type: string
    description: "The full filename of the audio asset in GCS."
    checks:
      - name: not_null
@bruin """

import logging
import pandas as pd
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

PROJECT_ID = "suara-pipeline"
BUCKET_NAME = "suara-lake-ananur"

def materialize():
    try:
        # Connect to GCS
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)

        logging.info(f"Reading files from bucket: {BUCKET_NAME}")

        # Read all blobs
        blobs = bucket.list_blobs()

        data = []

        for i, blob in enumerate(blobs, start=1):
            if blob.name.endswith(".wav"):
                data.append({
                    "id": i,
                    "audio_file_name": blob.name,
                    "gcs_uri": f"gs://{BUCKET_NAME}/{blob.name}",
                    "file_size_mb": round(blob.size / (1024 * 1024), 2) if blob.size else None,
                    "created_at": blob.time_created,
                    "updated_at": blob.updated
                })

        df = pd.DataFrame(data)

        logging.info(f"Found {len(df)} WAV files.")

        return df.sort_values("audio_file_name").reset_index(drop=True)

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise