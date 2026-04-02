"""@bruin
name: suara_sea.transcriptions
type: python
connection: gcp-default
materialization:
  type: table
depends:
  - suara_sea.stg_audio_metadata
description: "Transcribes audio files using Faster-Whisper."
owner: "data.engineer@suara-sea.com"
@bruin"""

import pandas as pd
from google.cloud import storage, bigquery
from faster_whisper import WhisperModel
import os

def materialize():
    # 1. Initialize the AI Model (Using 'tiny' model for CPU speed)
    print("Loading Hugging Face Whisper Model...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")

    # 2. Connect to Google Cloud
    storage_client = storage.Client(project="suara-pipeline")
    bq_client = bigquery.Client(project="suara-pipeline")
    bucket = storage_client.bucket("suara-lake-ananur")

    # 3. Ask the Data Warehouse which files to process
    # We limit to 3 files for our initial test run!
    query = """
        SELECT id, audio_file_name 
        FROM `suara-pipeline.suara_sea.stg_audio_metadata` 
        LIMIT 3
    """
    print("Fetching audio metadata from BigQuery...")
    df_meta = bq_client.query(query).to_dataframe()

    results = []

    # 4. Process the audio files
    for index, row in df_meta.iterrows():
        file_name = row['audio_file_name']
        file_id = row['id']
        
        print(f"\n[{index+1}/{len(df_meta)}] Processing: {file_name}")
        
        # Download physical file from the Data Lake to a temporary local file
        blob = bucket.blob(file_name)
        local_temp_path = f"/tmp/{file_name.split('/')[-1]}"
        blob.download_to_filename(local_temp_path)
        
        # Transcribe using Whisper, forcing Indonesian ('id')
        print("Transcribing audio...")
        segments, info = model.transcribe(local_temp_path, language="id", beam_size=5)
        
        # Combine the text segments
        full_text = " ".join([segment.text for segment in segments])
        print(f"Result: {full_text[:60]}...") # Print a preview
        
        # Save to our results list
        results.append({
            "audio_id": file_id,
            "file_name": file_name,
            "transcript": full_text.strip(),
            "language_detected": info.language,
            "language_probability": float(info.language_probability)
        })
        
        # Clean up the temporary file so we don't run out of storage
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)

    print("\nTranscription batch complete! Passing dataframe to Bruin...")
    
    # 5. Return the dataframe for Bruin to materialize into BigQuery
    return pd.DataFrame(results)
