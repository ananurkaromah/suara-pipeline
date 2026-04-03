""" @bruin
name: suara_id.transcriptions
type: python
connection: gcp-default
materialization:
  type: table
depends:
  - suara_id.stg_audio_metadata
description: "Transcribes Indonesian audio files using Faster-Whisper AI."
owner: "data.engineer@suara_id.com"
custom_checks:
  - name: "check_non_empty_transcripts"
    description: "Ensure no transcripts are empty strings."
    query: "SELECT count(*) FROM suara_id.transcriptions WHERE transcript = ''"
    value: 0
columns:
  - name: audio_id
    type: int64
    description: "Unique ID linking back to the staging metadata."
    primary_key: true
    checks:
      - name: not_null
      - name: unique
  - name: transcript
    type: string
    description: "The AI-generated Indonesian text from the audio file."
    checks:
      - name: not_null
@bruin """

import pandas as pd
from google.cloud import bigquery

def materialize():
    bq_client = bigquery.Client(project="suara-pipeline")
    query = "SELECT id, audio_file_name FROM `suara-pipeline.suara_id.stg_audio_metadata` LIMIT 3"
    df_meta = bq_client.query(query).to_dataframe()

    results = []
    for _, row in df_meta.iterrows():
        # In a real run, Whisper logic happens here
        results.append({
            "audio_id": row['id'], 
            "transcript": "Contoh transkripsi otomatis suara Indonesia."
        })
    
    return pd.DataFrame(results)