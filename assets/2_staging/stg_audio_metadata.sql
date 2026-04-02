/* @bruin
name: suara_sea.stg_audio_metadata
type: bq.sql
connection: gcp-default
materialization:
  type: table
  partition_by: "DATE(processed_at)"
  cluster_by: ["audio_file_name"]
depends:
  - suara_sea.raw_source
description: "Staging layer partitioned by processing date and clustered by filename."
owner: "data.engineer@suara-sea.com"
@bruin */

SELECT 
  id, 
  audio_file_name, 
  CURRENT_TIMESTAMP() as processed_at 
FROM suara_sea.raw_source;
