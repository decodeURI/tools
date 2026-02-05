# OJS Directory Scanner V20 – Deep Permutation 🚀

Mana tau kepake, brute force direktori OJS pake varian baru. Script ini otomatis ngeracik *subdomain* target sama *keywords* jadi wordlist dinamis dan nentuin responnya pake slesh {/}. 

Full async, sat-set. Logger? Gak ada wkwk.

![Preview Screenshot](https://github.com/decodeURI/tools/blob/main/Screenshot%202026-02-06%20033227.png?raw=true)

---

## 🛠️ Features
- **Dynamic Wordlist:** Gak pake wordlist statis sampah. Script ngeracik path berdasarkan nama domain target (Custom Permutation).
- **High Speed:** Full asynchronous pake `aiohttp` & `asyncio`. Gas 100-200 threads bodo amat.
- **Smart Detection:** Auto sortir status:
  - `[FOUND DIR]` (Redirect)
  - `[FORBIDDEN]` (403 - Folder ada tapi diproteksi)
  - `[LIVE INDEX]` (200 - Rejeki anak soleh, open directory)

## 🚀 Installation
Cukup install library buat koneksinya:
```bash
pip install aiohttp aiofiles
