# Lesson 18: Penanganan error dan fallback

**One-liner:** Rancang respons error yang menjaga kepercayaan pengguna.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Rencana Error Handling dan Fallback

## Learning goal

You will be able to: **Menyusun rencana penanganan error dan fallback yang aman.**

### Success criteria (observable)
- [ ] Tiga jenis error dicatat.
- [ ] Setiap error memiliki pesan pengguna dan langkah berikut.
- [ ] Satu fallback ditulis untuk kegagalan besar.

### Output you will produce
- **Deliverable:** Rencana Error Handling dan Fallback
- **Format:** Tabel error dan respons
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang mengelola error app AI
**Secondary persona(s):** Pengguna yang butuh penjelasan jelas
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Rencana yang menjelaskan jenis error, pesan pengguna, dan langkah berikut.
Fallback aman yang membantu pengguna saat sistem gagal.

### What it is not
Bukan log teknis saja.
Bukan proses tanpa komunikasi pengguna.

### 2-minute theory
- Error akan terjadi, tetapi pengalaman tetap bisa baik.
- Pesan jelas mengurangi frustrasi.
- Fallback menyelamatkan pengalaman saat gagal.

### Key terms
- **Error handling:** Cara sistem merespons error.
- **Fallback:** Respons cadangan saat error.

## Where

### Applies in
- API routes
- UI messages

### Does not apply in
- Copy pemasaran

### Touchpoints
- Error logs
- Pesan pengguna
- Tiket support

## When

### Use it when
- App mulai dipakai pengguna
- Anda menemukan error tak terduga

### Frequency
Setiap fitur baru

### Late signals
- Pengguna bingung tanpa pesan jelas
- Tiket support meningkat

## Why it matters

### Practical benefits
- Kepercayaan pengguna terjaga
- Support lebih efisien
- Produk lebih stabil

### Risks of ignoring
- Pengguna frustrasi
- Penggunaan turun

### Expectations
- Improves: kepercayaan dan pengalaman
- Does not guarantee: tanpa error

## How

### Step-by-step method
1. Catat 3 jenis error umum.
2. Tulis pesan pengguna untuk tiap error.
3. Tambahkan langkah berikut.
4. Buat fallback untuk error besar.
5. Log error untuk analisis.

### Do and don't

**Do**
- Gunakan bahasa sederhana
- Sertakan langkah berikut

**Don't**
- Menampilkan stack trace ke pengguna
- Menyalahkan pengguna

### Common mistakes and fixes
- **Mistake:** Pesan terlalu umum. **Fix:** Tambahkan konteks dan solusi.
- **Mistake:** Tidak ada fallback. **Fix:** Buat fallback dasar.

### Done when
- [ ] Error utama tercatat.
- [ ] Pesan pengguna ada.
- [ ] Fallback tersedia.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar error yang mungkin muncul
- Persona pengguna

### Steps
1. Tulis 3 error utama.
2. Tulis pesan dan langkah berikut.
3. Tambahkan fallback.

### Output format
| Field | Value |
|---|---|
| Error type | |
| User message | |
| Next step | |
| Fallback | |

> **Pro tip:** Pesan singkat dan jelas mengurangi frustrasi.

## Independent exercise (5 to 10 min)

### Task
Perbaiki satu pesan error agar lebih ramah.

### Output
Pesan error yang diperbaiki.

## Self-check (yes/no)

- [ ] Apakah jenis error dicatat?
- [ ] Apakah pesan pengguna jelas?
- [ ] Apakah ada fallback?
- [ ] Apakah error dicatat di log?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Error Handling UX**. NNGroup. 2024-01-01.
   Read: https://www.nngroup.com/articles/error-messages/

2. **Resilient Systems Basics**. AWS. 2024-01-01.
   Read: https://aws.amazon.com/builders-library/

## Read more (optional)

1. **Fallback Patterns**
   Why: Pola respons saat gagal.
   Read: https://aws.amazon.com/builders-library/
