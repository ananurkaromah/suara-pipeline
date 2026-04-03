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

import pandas as pd
from google.cloud import storage

def materialize():
    storage_client = storage.Client(project="suara-pipeline")
    bucket = storage_client.bucket("suara-lake-ananur")
    blobs = bucket.list_blobs(max_results=100)
    
    data = [{"id": i + 1, "audio_file_name": b.name} for i, b in enumerate(blobs) if b.name.endswith('.wav')]
    return pd.DataFrame(data)