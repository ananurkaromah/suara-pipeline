""" @bruin
name: suara_id.transcriptions
type: python
connection: gcp-default
materialization:
  type: table
depends:
  - suara_id.stg_audio_metadata
description: "Transcribes Indonesian audio files using Faster-Whisper AI."
owner: "ana@suara-id.com"
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

import logging
import tempfile
import pandas as pd

from faster_whisper import WhisperModel
from google.cloud import bigquery
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

PROJECT_ID = "suara-pipeline"
BUCKET_NAME = "suara-lake-ananur"

def materialize():

    # Initialize clients
    bq_client = bigquery.Client(project=PROJECT_ID)
    storage_client = storage.Client(project=PROJECT_ID)

    bucket = storage_client.bucket(BUCKET_NAME)

    # Load Whisper model
    logging.info("Loading Faster-Whisper model...")
    model = WhisperModel(
        "small",
        device="cpu",
        compute_type="int8"
    )

    # Load metadata
    query = """
    SELECT id, audio_file_name
    FROM `suara-pipeline.suara_id.stg_audio_metadata`
    """

    df_meta = bq_client.query(query).to_dataframe()

    logging.info(f"Found {len(df_meta)} audio files.")

    results = []

    for _, row in df_meta.iterrows():

        audio_id = row["id"]
        audio_file = row["audio_file_name"]

        try:
            logging.info(f"Processing: {audio_file}")

            # Download audio temporarily
            blob = bucket.blob(audio_file)

            with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:

                blob.download_to_filename(temp_audio.name)

                # Run transcription
                segments, info = model.transcribe(
                    temp_audio.name,
                    language="id"
                )

                transcript = " ".join(
                    segment.text.strip()
                    for segment in segments
                ).strip()

                # Skip empty transcript
                if not transcript:
                    logging.warning(f"Empty transcript: {audio_file}")
                    continue

                results.append({
                    "audio_id": audio_id,
                    "audio_file_name": audio_file,
                    "transcript": transcript,
                    "language": info.language,
                    "duration": info.duration,
                    "model_used": "faster-whisper-small"
                })

        except Exception as e:
            logging.error(f"Failed processing {audio_file}: {str(e)}")

    logging.info(f"Successfully transcribed {len(results)} files.")

    return pd.DataFrame(results)