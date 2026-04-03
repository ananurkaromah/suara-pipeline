import os
from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage

def main():
    # --- Configuration ---
    dataset_name = "hengkymulyono/indonesian-speech-with-accents-5-ethnic-groups"
    local_download_path = "/tmp/raw_audio"
    gcp_project = "suara-pipeline"
    bucket_name = "suara-lake-ananur"

    print("1. Authenticating Kaggle and downloading dataset...")
    # The Kaggle API automatically looks for ~/.kaggle/kaggle.json
    # (Ensure your Dockerfile still copies kaggle.json to this location)
    api = KaggleApi()
    api.authenticate()
    
    # Download and unzip directly via the Python API
    api.dataset_download_files(dataset_name, path=local_download_path, unzip=True)
    print(f"Dataset downloaded and unzipped to {local_download_path}")

    print("2. Connecting to Google Cloud Storage...")
    # Bruin automatically handles GCP authentication
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)

    print(f"3. Uploading files to gs://{bucket_name}/...")
    upload_count = 0
    
    # Walk through the unzipped directory and upload .wav files
    for root, dirs, files in os.walk(local_download_path):
        for file in files:
            if file.endswith(".wav"):
                local_file_path = os.path.join(root, file)
                
                # Upload the file to the root of the GCS bucket
                blob = bucket.blob(file) 
                blob.upload_from_filename(local_file_path)
                upload_count += 1
                
                if upload_count % 500 == 0:
                    print(f"Uploaded {upload_count} files...")

    print(f"Success! {upload_count} audio files uploaded to GCS.")

    print("4. Cleaning up local temporary files...")
    # Clean up the downloaded files to free up Docker container space
    for root, dirs, files in os.walk(local_download_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
            
    print("Pipeline Extraction Complete.")

# Bruin will execute the script top-to-bottom for non-materialized Python assets
if __name__ == "__main__":
    main()