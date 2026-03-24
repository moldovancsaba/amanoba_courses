# Lesson 10: Dasar OpenAI API dan pola aman

**One-liner:** Buat panggilan OpenAI API yang andal dengan perlindungan dasar.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Panggilan OpenAI yang Berfungsi dan Penanganan Error

## Learning goal

You will be able to: **Mengimplementasikan request dasar OpenAI API dengan default aman dan penanganan error.**

### Success criteria (observable)
- [ ] Request mengembalikan respons untuk input contoh.
- [ ] Error ditangani dengan pesan yang aman.
- [ ] API key disimpan di env variable.

### Output you will produce
- **Deliverable:** Panggilan OpenAI yang Berfungsi dan Penanganan Error
- **Format:** Potongan kode dan test log
- **Where saved:** Repo dan catatan kursus di folder kursus

## Who

**Primary persona:** Digital nomad yang membangun app AI
**Secondary persona(s):** Pengguna awal yang mengandalkan output stabil
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Panggilan server side kecil ke OpenAI API dengan default yang aman.
Ia mengembalikan respons yang berguna dan gagal dengan cara yang dapat dipahami.

### What it is not
Bukan sistem agent penuh atau orkestrasi kompleks.
Bukan pengganti validasi produk.

### 2-minute theory
- Default aman mengurangi perilaku tak terduga dan biaya.
- Penanganan error yang jelas menjaga kepercayaan pengguna.
- Env variables menjaga secrets tetap keluar dari codebase.

### Key terms
- **API key:** Kunci rahasia untuk autentikasi request.
- **Fallback:** Tanggapan cadangan saat API gagal.

## Where

### Applies in
- Server routes
- Backend services

### Does not apply in
- Penyimpanan rahasia di client

### Touchpoints
- API route
- Error logs
- Env configuration

## When

### Use it when
- Anda menambahkan fitur AI
- Anda membutuhkan respons awal yang stabil

### Frequency
Sekali per produk, revisi saat fitur bertambah

### Late signals
- Error sering tanpa pesan jelas
- Secrets tercommit ke repo

## Why it matters

### Practical benefits
- Debugging lebih cepat saat terjadi error
- Deploy lebih aman tanpa kebocoran key
- Pengalaman pengguna lebih baik saat API lambat

### Risks of ignoring
- Kebocoran API key dan biaya tak terduga
- Error yang tidak jelas menurunkan kepercayaan

### Expectations
- Improves: stabilitas dan kepercayaan
- Does not guarantee: output sempurna

## How

### Step-by-step method
1. Simpan API key di env variable.
2. Kirim request dengan prompt singkat.
3. Tambahkan timeout dan penanganan error.
4. Kembalikan fallback saat gagal.
5. Catat request id untuk tracing.

### Do and don't

**Do**
- Gunakan prompt singkat yang bisa diuji
- Log error dengan konteks request

**Don't**
- Menaruh API key di client
- Menyembunyikan error dari log

### Common mistakes and fixes
- **Mistake:** Key ada di code. **Fix:** Pindahkan ke env dan rotasi key.
- **Mistake:** Tidak ada fallback. **Fix:** Tambahkan pesan cadangan.

### Done when
- [ ] Request berhasil dengan input contoh.
- [ ] Error mengembalikan pesan jelas.
- [ ] API key ada di env.

## Guided exercise (10 to 15 min)

### Inputs
- OpenAI API key di env
- Prompt contoh

### Steps
1. Tulis function untuk request.
2. Tambahkan error handling dan fallback.
3. Jalankan test dan catat hasil.

### Output format
| Field | Value |
|---|---|
| Input prompt | |
| Response sample | |
| Error handling | |
| Fallback message | |

> **Pro tip:** Simpan request id di log untuk memudahkan tracing.

## Independent exercise (5 to 10 min)

### Task
Ubah prompt dan pastikan output tetap stabil.

### Output
Test log dengan prompt baru dan respons.

## Self-check (yes/no)

- [ ] Apakah API key disimpan di env?
- [ ] Apakah error mengembalikan pesan aman?
- [ ] Apakah fallback tersedia?
- [ ] Apakah test run dicatat?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Terminal

## Bibliography (sources used)

1. **OpenAI API Docs**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs

2. **OWASP API Security Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-api-security/

## Read more (optional)

1. **OpenAI Safety Best Practices**
   Why: Praktik aman untuk fitur AI.
   Read: https://platform.openai.com/docs/guides/safety-best-practices
