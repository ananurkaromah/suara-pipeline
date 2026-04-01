"""@bruin
name: transcriber
type: python
connection: gcp-default
depends:
  - suara_sea.stg_audio_metadata
@bruin"""

def main():
    print("Suara-SEA Intelligence Layer: Online")

if __name__ == "__main__":
    main()
