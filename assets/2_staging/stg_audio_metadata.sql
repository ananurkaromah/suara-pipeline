/* @bruin
name: suara_sea.stg_audio_metadata
type: bq.sql
connection: gcp-default
materialization:
  type: table
depends:
  - suara_sea.raw_source
@bruin */

SELECT * FROM suara_sea.raw_source;
