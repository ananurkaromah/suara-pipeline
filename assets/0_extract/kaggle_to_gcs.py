""" @bruin
name: suara_id.kaggle_to_gcs
type: python
connection: gcp-default
description: "Extracts the Indonesian Ethnic Speech dataset from Kaggle and loads it into the GCS Data Lake."
owner: "data.engineer@suara_id.com"
@bruin """

import os
from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage

def main():
    dataset_name = "hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups"
    local_download_path = "/tmp/raw_audio"
    gcp_project = "suara-pipeline"
    bucket_name = "suara-lake-ananur"

    print("1. Authenticating Kaggle and downloading dataset...")
    api = KaggleApi()
    api.authenticate()
    
    # Create temp directory if it doesn't exist
    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)
    
    api.dataset_download_files(dataset_name, path=local_download_path, unzip=True)
    print(f"Dataset downloaded to {local_download_path}")

    print("2. Connecting to Google Cloud Storage...")
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)

    print(f"3. Uploading .wav files to gs://{bucket_name}/...")
    upload_count = 0
    
    for root, _, files in os.walk(local_download_path):
        for file in files:
            if file.endswith(".wav"):
                local_file_path = os.path.join(root, file)
                # Keep it simple: upload to the root of the bucket
                blob = bucket.blob(file) 
                blob.upload_from_filename(local_file_path)
                upload_count += 1
                
                if upload_count % 100 == 0:
                    print(f"Uploaded {upload_count} files...")

    print(f"Success! {upload_count} audio files uploaded to GCS.")

    # 4. Cleanup
    import shutil
    shutil.rmtree(local_download_path)
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
