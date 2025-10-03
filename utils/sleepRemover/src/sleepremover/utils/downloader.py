import aiohttp
import aiofiles
import asyncio
import json
from pathlib import Path
from tqdm import tqdm


async def download_file(session: aiohttp.ClientSession, file_info: dict, cache_dir: Path, pbar: tqdm) -> bool:
    """Download a single language file asynchronously."""
    file_name = file_info['name']
    file_url = file_info['download_url']
    
    try:
        async with session.get(file_url) as response:
            response.raise_for_status()
            text = await response.text()
            data = json.loads(text)
            
            file_path = cache_dir / file_name
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            pbar.update(1)
            return True
            
    except Exception as e:
        print(f"Failed to download {file_name}: {e}")
        pbar.update(1)
        return False


async def download_all_files(json_files: list, cache_dir: Path) -> int:
    """Download all language files asynchronously."""
    connector = aiohttp.TCPConnector(limit=20, limit_per_host=10)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        with tqdm(total=len(json_files), desc="Downloading language files") as pbar:
            tasks = [download_file(session, file_info, cache_dir, pbar) for file_info in json_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for result in results if result is True)
            return successful
