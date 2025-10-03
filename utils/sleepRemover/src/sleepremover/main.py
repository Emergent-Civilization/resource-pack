import argparse
from sleepremover.core.languages import get_language_files, process_sleep_messages

def main():
    parser = argparse.ArgumentParser(description="Sleep Remover - Process Minecraft language files")
    parser.add_argument("--output-path", "-o",
                       required=True,
                       help="Output namespace path of the resource pack for the language files")
    parser.add_argument("--skip-download", "-s", 
                       action="store_true", 
                       help="Skip downloading language files (use existing cache)")
    
    args = parser.parse_args()
    
    print("Sleep Remover - Processing Minecraft language files")
    print(f"Output namespace path of the resource pack for the language files: {args.output_path}")
    
    if not args.skip_download:
        print("\nStep 1: Downloading language files...")
        language_files = get_language_files()
        print(f"Language files downloaded to: {language_files}")
    else:
        print("\nSkipping download (using existing cache)")
    
    print("\nStep 2: Processing sleep messages...")
    process_sleep_messages(args.output_path + "/lang")
    
    print(f"\nCompleted! Language files saved to: {args.output_path}/lang")

if __name__ == "__main__":
    main()