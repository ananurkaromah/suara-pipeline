/*
@bruin
name: staging.audio_metadata
type: bq.sql
connection: gcp-default
depends:
  - ingestion.raw_source
@bruin
*/
SELECT * FROM {{ ref('ingestion.raw_source') }};
