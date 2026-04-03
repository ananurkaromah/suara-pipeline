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
    description: "Ensure that only .wav audio files are ingested into the raw layer."
    query: "SELECT count(*) FROM suara_id.raw_source WHERE audio_file_name NOT LIKE '%.wav'"
    value: 0
columns:
  - name: id
    type: int64
    description: "Unique integer identifier for each audio record generated during ingestion."
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: audio_file_name
    type: string
    description: "The full filename of the audio asset as it exists in the GCS bucket."
    checks:
      - name: not_null
@bruin """

import pandas as pd
from google.cloud import storage

def materialize():
    print("Connecting to GCS Data Lake...")
    # Initialize the GCS client
    # Project ID should match your GCP Console project name
    storage_client = storage.Client(project="suara-pipeline")
    bucket = storage_client.bucket("suara-lake-ananur")
    
    # List the blobs (files) currently in the bucket
    # We limit to 100 for development; remove 'max_results' for full production run
    blobs = bucket.list_blobs(max_results=100)
    
    data = []
    for i, blob in enumerate(blobs):
        # Filter to ensure we only ingest audio metadata
        if blob.name.endswith('.wav'):
            data.append({
                "id": i + 1,
                "audio_file_name": blob.name
            })
            
    print(f"Found {len(data)} audio files in the Data Lake.")
    
    # Return the dataframe to Bruin for BigQuery materialization
    return pd.DataFrame(data)