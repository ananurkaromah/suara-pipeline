import pandas as pd
from google.cloud import storage, bigquery
from faster_whisper import WhisperModel
import os
import uuid # Library bawaan Python untuk membuat ID unik

def materialize():
    # 1. Initialize the AI Model
    print("Loading Hugging Face Whisper Model...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")

    # 2. Connect to Google Cloud
    storage_client = storage.Client(project="suara-pipeline")
    bq_client = bigquery.Client(project="suara-pipeline")
    bucket = storage_client.bucket("suara-lake-ananur")

    # 3. Ask the Data Warehouse which files to process
    # Perbaikan: Sesuaikan dengan nama kolom baru di stg_audio_metadata
    query = """
        SELECT stg.audio_id, stg.file_path 
        FROM `suara-pipeline.suara_id.stg_audio_metadata` AS stg
        LEFT JOIN `suara-pipeline.suara_id.transcriptions` AS tr
          ON stg.audio_id = tr.audio_id
        WHERE tr.audio_id IS NULL
        LIMIT 3
    """
    print("Fetching unprocessed audio metadata from BigQuery...")
    try:
        df_meta = bq_client.query(query).to_dataframe()
    except Exception as e:
        # Jika tabel transcription belum ada (run pertama), gunakan query dasar
        print("First run detected, fetching base metadata...")
        fallback_query = """
            SELECT audio_id, file_path 
            FROM `suara-pipeline.suara_id.stg_audio_metadata` 
            LIMIT 3
        """
        df_meta = bq_client.query(fallback_query).to_dataframe()

    if df_meta.empty:
        print("No new audio files to process. Exiting cleanly.")
        return pd.DataFrame()

    results = []

    # 4. Process the audio files
    for index, row in df_meta.iterrows():
        file_name = row['file_path']
        file_id = row['audio_id']
        
        print(f"\n[{index+1}/{len(df_meta)}] Processing: {file_name}")
        
        blob = bucket.blob(file_name)
        local_temp_path = f"/tmp/{file_name.split('/')[-1]}"
        blob.download_to_filename(local_temp_path)
        
        print("Transcribing audio...")
        segments, info = model.transcribe(local_temp_path, language="id", beam_size=5)
        
        full_text = " ".join([segment.text for segment in segments])
        print(f"Result: {full_text[:60]}...")
        
        # Perbaikan: Cocokkan keys ini persis dengan yang ada di header Bruin!
        results.append({
            "transcription_id": f"trx_{uuid.uuid4().hex[:8]}", # Membuat ID Unik
            "audio_id": str(file_id),
            "transcription_text": full_text.strip()
        })
        
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)

    print("\nTranscription batch complete! Passing dataframe to Bruin...")
    return pd.DataFrame(results)