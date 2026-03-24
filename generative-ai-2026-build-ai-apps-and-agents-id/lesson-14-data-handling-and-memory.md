# Lesson 14: Penanganan data dan memory

**One-liner:** Kelola data pengguna secara aman dan terukur.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Rencana Data dan Memory

## Learning goal

You will be able to: **Mendesain rencana data dan memory yang menjaga privasi.**

### Success criteria (observable)
- [ ] Jenis data dan tujuan penggunaannya ditulis.
- [ ] Ada aturan retensi dan penghapusan data.
- [ ] Setidaknya satu risiko privasi dan mitigasinya dicatat.

### Output you will produce
- **Deliverable:** Rencana Data dan Memory
- **Format:** Tabel data dan ringkasan kebijakan
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menangani data app AI
**Secondary persona(s):** Pengguna yang peduli privasi
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Daftar jenis data yang dikumpulkan, alasan, dan cara penggunaannya.
Rencana memory yang menjelaskan apa yang disimpan dan berapa lama.

### What it is not
Bukan dokumen legal lengkap.
Bukan menyimpan semua data tanpa batas.

### 2-minute theory
- Data yang tidak terkontrol meningkatkan risiko privasi.
- Memory singkat bisa meningkatkan UX tanpa menyimpan terlalu banyak.
- Aturan penghapusan data meningkatkan kepercayaan.

### Key terms
- **Memory:** Data konteks kecil untuk memperbaiki percakapan.
- **Retention:** Lama penyimpanan data sebelum dihapus.

## Where

### Applies in
- Database pengguna
- Logs dan analytics

### Does not apply in
- Data uji internal tanpa pengguna nyata

### Touchpoints
- Database
- Privacy settings
- Permintaan ekspor atau penghapusan

## When

### Use it when
- Anda mulai menyimpan data pengguna
- Anda mengelola percakapan atau history

### Frequency
Tinjau saat ada perubahan produk

### Late signals
- Tidak ada aturan penghapusan
- Keluhan privasi dari pengguna

## Why it matters

### Practical benefits
- Privasi lebih kuat
- Risiko legal lebih rendah
- Kepercayaan pengguna meningkat

### Risks of ignoring
- Kebocoran data
- Ketidakmampuan memenuhi permintaan penghapusan

### Expectations
- Improves: privasi dan kontrol
- Does not guarantee: perlindungan hukum penuh

## How

### Step-by-step method
1. Daftarkan semua jenis data yang dikumpulkan.
2. Tulis alasan penggunaan tiap data.
3. Tentukan periode retensi.
4. Sediakan proses penghapusan data.
5. Catat satu risiko privasi dan mitigasinya.

### Do and don't

**Do**
- Kumpulkan data seperlunya
- Tetapkan retensi yang jelas

**Don't**
- Menyimpan data tanpa batas
- Mengumpulkan data tanpa alasan

### Common mistakes and fixes
- **Mistake:** Tidak ada retensi. **Fix:** Tentukan durasi penyimpanan.
- **Mistake:** Memory jangka panjang tanpa izin. **Fix:** Gunakan opt in.

### Done when
- [ ] Jenis data dan tujuan ditulis.
- [ ] Retensi dijelaskan.
- [ ] Risiko privasi dicatat.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar fitur data
- Kebutuhan privasi

### Steps
1. Tulis 5 jenis data.
2. Tentukan retensi tiap data.
3. Tambahkan risiko dan mitigasi.

### Output format
| Field | Value |
|---|---|
| Data type | |
| Purpose | |
| Retention | |
| Risk and mitigation | |

> **Pro tip:** Prioritaskan data minimum yang benar benar dibutuhkan.

## Independent exercise (5 to 10 min)

### Task
Tulis ringkasan privasi satu paragraf untuk pengguna.

### Output
Ringkasan privasi.

## Self-check (yes/no)

- [ ] Apakah jenis data jelas?
- [ ] Apakah retensi tertulis?
- [ ] Apakah ada proses penghapusan?
- [ ] Apakah risiko privasi dicatat?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Data Retention Best Practices**. Mozilla. 2024-01-01.
   Read: https://developer.mozilla.org/en-US/docs/Web/Privacy

2. **OWASP Privacy Risks**. OWASP. 2024-01-01.
   Read: https://owasp.org/

## Read more (optional)

1. **Privacy by Design Overview**
   Why: Prinsip privasi sejak awal.
   Read: https://www.ipc.on.ca/privacy-by-design/
