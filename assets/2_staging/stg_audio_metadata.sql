/* @bruin
name: suara_id.stg_audio_metadata
type: bq.sql
connection: gcp-default
materialization:
  type: table
  partition_by: "DATE(processed_at)"
  cluster_by: ["audio_file_name"]
depends:
  - suara_id.raw_source
description: "Staging layer partitioned by processing date and clustered by filename."
owner: "data.engineer@suara_id.com"
columns:
  - name: id
    type: int64
    description: "Primary key inherited from raw source"
  - name: audio_file_name
    type: string
    description: "The name of the audio file"
  - name: processed_at
    type: timestamp
    description: "Timestamp of when the record was processed"
@bruin */

SELECT 
  id, 
  audio_file_name, 
  CURRENT_TIMESTAMP() as processed_at 
FROM suara_id.raw_source;
