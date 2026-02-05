import aiohttp
import asyncio
import sys
import random
import aiofiles
import os
from urllib.parse import urlparse

GREEN, CYAN, YELLOW, RED, PURPLE, GRAY, RESET = "\033[92m", "\033[96m", "\033[93m", "\033[91m", "\033[95m", "\033[90m", "\033[0m"

KEYWORDS = [
    'archive', 'archives', 'ojs3.3', 'content', 'data', 
    'dokumen', 'download', 'file', 'files', 'internal', 'ejurnal', 
    'ojs-data', 'ojs-files', 'jurnal', 'ojs_data', 'ojs_files', 
    'journal', 'ojsdata', 'ojs', 'private', 'repository', 
    'storage', 'ojsUpload', 'journals', 'upload', 'uploads'
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
]

TIMEOUT_CONFIG = aiohttp.ClientTimeout(total=20, connect=7, sock_read=10)
CONCURRENCY = 100 

def generate_dynamic_payloads(domain_url):
    """
    LOGIKA DEEP PERMUTATION:
    Mencoba SEMUA kombinasi keyword1 + separator + keyword2
    """
    parsed = urlparse(domain_url)
    netloc = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
    sub = netloc.split('.')[0] if '.' in netloc else ""
    
    final_payloads = set()
    separators = ['', '_', '-']

    for kw in KEYWORDS:
        final_payloads.add(f"/{kw}")
    
    if sub:
        for kw in KEYWORDS:
            for sep in separators:
                final_payloads.add(f"/{sub}{sep}{kw}")
                final_payloads.add(f"/{kw}{sep}{sub}")
    
    for k1 in KEYWORDS:
        for k2 in KEYWORDS:
            if k1 != k2:
                for sep in separators:

                    final_payloads.add(f"/{k1}{sep}{k2}")
    
    return list(final_payloads)

async def check_url(session, base_url, path):
    target_url = base_url.rstrip('/') + path
    
    sys.stdout.write(f"\r{GRAY}[CHECKING]{RESET} -> {path[:40]}{' ' * 10}")
    sys.stdout.flush()
    
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        async with session.get(target_url, headers=headers, timeout=TIMEOUT_CONFIG, allow_redirects=False, ssl=False) as resp:
            
            if resp.status in [301, 302]:
                loc = resp.headers.get('Location', '')
                if path in loc:
                    print(f"\r{GREEN}[FOUND DIR]{RESET} -> {target_url}/ (Redirect Valid){' ' * 30}")
                    async with aiofiles.open("found_dirs.txt", "a") as f:
                        await f.write(target_url + "/\n")
                    return True

            if resp.status == 403:
                print(f"\r{PURPLE}[FORBIDDEN]{RESET} -> {target_url} (Valid Folder){' ' * 30}")
                async with aiofiles.open("found_forbidden.txt", "a") as f:
                    await f.write(target_url + "\n")
                return True

            if resp.status == 200:
                text = await resp.text(errors='ignore')
                if any(x in text.lower() for x in ["index of", "parent directory"]):
                    print(f"\r{CYAN}[LIVE INDEX]{RESET} -> {target_url}{' ' * 30}")
                    async with aiofiles.open("found_index.txt", "a") as f:
                        await f.write(target_url + "\n")
                    return True
    except:
        pass
    return False

async def worker(queue, session):
    while True:
        task = await queue.get()
        if task is None: break
        await check_url(session, task[0], task[1])
        queue.task_done()

async def start_scanning():
    print(f"\n{CYAN}Target Domain (Contoh: jurnal.komdigi.go.id) > {RESET}", end="")
    inp = input().strip()
    if not inp: return

    base_url = inp if inp.startswith('http') else 'https://' + inp
    
    print(f"{YELLOW}[*] Generating Deep Wordlist...{RESET}")
    payloads = generate_dynamic_payloads(base_url)
    
    queue = asyncio.Queue()
    for p in payloads:
        queue.put_nowait((base_url, p))

    print(f"{YELLOW}[*] Total Antrean: {queue.qsize()} kombinasi{RESET}")
    print(f"{YELLOW}[*] Memulai Scan dengan {CONCURRENCY} Workers...{RESET}\n")

    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        workers = [asyncio.create_task(worker(queue, session)) for _ in range(CONCURRENCY)]
        await queue.join()
        for _ in range(CONCURRENCY): await queue.put(None)
        await asyncio.gather(*workers)

    print(f"\n{GREEN}[DONE] Selesai! Cek file found_*.txt{RESET}")

def main():
    if sys.platform == 'win32':
        os.system('color')
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    while True:
        print(f"\n{YELLOW}========================================")
        print("    OJS DIRECTORY SCANNER V20.0 DEEP    ")
        print(f"========================================{RESET}")
        print("1. Scanner (Full Cross-Keyword Permutation)")
        print("2. Keluar")
        c = input(f"\nPilih menu > ")
        if c == '1': asyncio.run(start_scanning())
        elif c == '2': break

if __name__ == "__main__":
    main()
