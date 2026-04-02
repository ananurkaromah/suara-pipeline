"""@bruin
name: suara_sea.raw_source
type: python
connection: gcp-default
materialization:
  type: table
description: "Pulls a list of audio files from the GCS Data Lake into BigQuery."
owner: "data.engineer@suara-sea.com"
columns:
  - name: id
    type: int64
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: audio_file_name
    type: string
    checks:
      - name: not_null
@bruin"""

import pandas as pd
from google.cloud import storage

def materialize():
    print("Connecting to GCS Data Lake...")
    # Initialize the GCS client (Bruin passes the credentials automatically)
    storage_client = storage.Client(project="suara-pipeline")
    bucket = storage_client.bucket("suara-lake-ananur")
    
    # List the blobs (files). We limit to 100 for fast development testing.
    blobs = bucket.list_blobs(max_results=100)
    
    data = []
    for i, blob in enumerate(blobs):
        # We only want to log actual audio files
        if blob.name.endswith('.wav'):
            data.append({
                "id": i + 1,
                "audio_file_name": blob.name
            })
            
    print(f"Found {len(data)} audio files for ingestion.")
    
    # Return the dataframe so Bruin can build the BigQuery table!
    return pd.DataFrame(data)
