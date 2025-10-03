import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import List
from pathlib import Path
import asyncio
from ..utils.downloader import download_all_files


def get_language_codes() -> List[str]:
    """
    Extract Minecraft language codes from the Minecraft Wiki.
    
    Returns:
        List[str]: A list of valid Minecraft language codes
    """
    url = "https://minecraft.wiki/w/Language"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'data-description': 'Current language list'})
        
        if not table:
            raise ValueError("Could not find the language table on the page")
        
        language_codes = []
        rows = table.find_all('tr') # type: ignore
        
        for row in tqdm(rows, desc="Extracting language codes"):
            cells = row.find_all('td')
            
            if len(cells) < 6:
                continue
                
            first_cell = cells[0].get_text(strip=True)
            if not first_cell.isdigit():
                continue
                
            if len(cells) > 4:
                language_code = cells[4].get_text(strip=True)
                
                if language_code and language_code != '–':
                    if '‌[JEonly]' in language_code:
                        je_code = language_code.split('‌[JEonly]')[0]
                        if je_code and je_code.count('_') == 1 and len(je_code.split('_')) == 2:
                            language_codes.append(je_code)
                    elif (language_code.count('_') == 0 and 
                          language_code.isalpha() and 
                          len(language_code) >= 2):
                        language_codes.append(language_code)
                    elif (language_code.count('_') == 1 and 
                          len(language_code.split('_')) == 2 and
                          all(part.isalpha() and len(part) >= 2 for part in language_code.split('_'))):
                        language_codes.append(language_code)
        
        return language_codes
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch the page: {e}")
    except Exception as e:
        raise Exception(f"Error parsing the page: {e}")
    
def get_language_files() -> str:
    """
    Download all Minecraft language files from the GitHub repository to .cache/languages directory.
    Uses async downloads for much faster performance.
    
    Returns:
        str: Path to the .cache/languages folder containing the downloaded language files
    """
    repo_url = "https://api.github.com/repos/toxicity188/all-minecraft-language/contents"
    cache_dir = Path(".cache/languages")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        files = response.json()
        
        json_files = [f for f in files if f['name'].endswith('.json') and f['name'] != 'README.md']
        
        print(f"Found {len(json_files)} language files to download...")
        
        # Run async download
        successful = asyncio.run(download_all_files(json_files, cache_dir))
        
        print(f"Successfully downloaded {successful}/{len(json_files)} language files")
        print(f"Language files saved to: {cache_dir.absolute()}")
        return str(cache_dir.absolute())
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch repository contents: {e}")
    except Exception as e:
        raise Exception(f"Error downloading language files: {e}")


def process_sleep_messages(output_path: str) -> None:
    """
    Process sleep messages for all language codes.
    Creates output_path/language_code.json files with sleep.players_sleeping values.
    
    Args:
        output_path: Path where to save the language files (required)
    """
    import json
    import re
    
    # Get all language codes
    language_codes = get_language_codes()
    
    # Create output directory
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load fallback (en_gb) data
    cache_dir = Path(".cache/languages")
    fallback_file = cache_dir / "en_gb.json"
    
    if not fallback_file.exists():
        raise Exception("Fallback file en_gb.json not found in cache. Run get_language_files() first.")
    
    with open(fallback_file, 'r', encoding='utf-8') as f:
        fallback_data = json.load(f)
    
    fallback_sleep_msg = fallback_data.get("sleep.players_sleeping", "%s/%s players sleeping")
    
    print(f"Processing {len(language_codes)} language codes...")
    
    for lang_code in tqdm(language_codes, desc="Processing sleep messages"):
        # Check if language file exists in cache
        lang_file = cache_dir / f"{lang_code}.json"
        
        if lang_file.exists():
            # Load language-specific data
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            sleep_msg = lang_data.get("sleep.players_sleeping", fallback_sleep_msg)
        else:
            # Use fallback
            sleep_msg = fallback_sleep_msg
        
        # Handle different placeholder patterns
        processed_msg = sleep_msg
        
        # First try to replace %s/%s with ???
        if "%s/%s" in processed_msg:
            processed_msg = processed_msg.replace("%s/%s", "???")
        
        # Replace %1$s, %2$s, etc. with ??
        import re
        processed_msg = re.sub(r'%\d+\$s', '??', processed_msg)
        
        # Replace remaining %s with ??
        processed_msg = processed_msg.replace("%s", "??")
        
        # Replace %d with ??
        processed_msg = processed_msg.replace("%d", "??")
        
        # Create output file
        output_file = output_dir / f"{lang_code}.json"
        output_data = {
            "sleep.players_sleeping": processed_msg
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(language_codes)} language files")
    print(f"Output saved to: {output_dir.absolute()}")
    
    # Check for unmodified files
    unmodified_files = []
    for lang_code in language_codes:
        output_file = output_dir / f"{lang_code}.json"
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sleep_msg = data.get("sleep.players_sleeping", "")
                # Check for any type of placeholder: %s, %1$s, %2$s, %d, etc.
                if "%" in sleep_msg and ("s" in sleep_msg or "d" in sleep_msg):
                    unmodified_files.append((lang_code, sleep_msg))
    
    if unmodified_files:
        print(f"\nWARNING: Found {len(unmodified_files)} files with unmodified placeholders:")
        for lang_code, msg in unmodified_files:
            print(f"  - {lang_code}: {msg}")
    else:
        print("\nSUCCESS: All files processed successfully - no unmodified placeholders found!")