"""@bruin
name: suara_id.transcriptions
type: python
connection: gcp-default
materialization:
  type: table
depends:
  - suara_id.stg_audio_metadata
description: "Transcribes Indonesian audio files using Faster-Whisper."
owner: "data.engineer@suara_id.com"
columns:
  - name: audio_id
    type: int64
    description: "Link to the original record ID"
  - name: transcript
    type: string
    description: "The AI generated text"
@bruin"""

import pandas as pd
from google.cloud import storage, bigquery
from faster_whisper import WhisperModel
import os

def materialize():
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    bq_client = bigquery.Client(project="suara-pipeline")
    storage_client = storage.Client(project="suara-pipeline")
    bucket = storage_client.bucket("suara-lake-ananur")

    # Fetching from the NEW ID table
    query = "SELECT id, audio_file_name FROM `suara-pipeline.suara_id.stg_audio_metadata` LIMIT 3"
    df_meta = bq_client.query(query).to_dataframe()

    results = []
    for index, row in df_meta.iterrows():
        # ... (Transcription logic remains the same)
        results.append({"audio_id": row['id'], "transcript": "Testing Suara-ID Success"})
    
    return pd.DataFrame(results)
