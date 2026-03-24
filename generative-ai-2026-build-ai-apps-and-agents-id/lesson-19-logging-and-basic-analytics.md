# Lesson 19: Logging dan basic analytics

**One-liner:** Catat event penting untuk memahami penggunaan dan error.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Rencana Logging dan Metrik Dasar

## Learning goal

You will be able to: **Memilih event penting untuk logging dan metrik dasar produk.**

### Success criteria (observable)
- [ ] Ada 5 event penting yang dicatat.
- [ ] Setiap event memiliki tujuan dan contoh.
- [ ] Ada 2 metrik dasar yang ditulis.

### Output you will produce
- **Deliverable:** Rencana Logging dan Metrik Dasar
- **Format:** Tabel event dan metrik
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang memantau kesehatan produk
**Secondary persona(s):** Tim yang bergantung pada data
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Daftar event penting untuk memahami penggunaan dan error.
Metrik dasar untuk menilai kesehatan produk.

### What it is not
Bukan sistem analytics besar.
Bukan logging semua hal tanpa seleksi.

### 2-minute theory
- Logging memberi visibilitas penggunaan nyata.
- Metrik dasar menunjukkan apakah produk berjalan baik.
- Logging yang fokus lebih berguna daripada data berlebihan.

### Key terms
- **Event:** Tindakan yang dicatat dalam sistem.
- **Metric:** Ukuran untuk menilai kesehatan produk.

## Where

### Applies in
- Backend events
- Product usage

### Does not apply in
- Demo internal tanpa data nyata

### Touchpoints
- Event logs
- Analytics dashboard
- Alerts

## When

### Use it when
- Anda ingin memahami penggunaan
- Anda butuh indikator kesehatan produk

### Frequency
Setiap rilis fitur baru

### Late signals
- Tidak tahu titik drop pengguna
- Error muncul tanpa diketahui

## Why it matters

### Practical benefits
- Keputusan produk lebih data-driven
- Debugging lebih cepat
- Pemahaman pengguna lebih baik

### Risks of ignoring
- Keputusan tanpa data
- Error tidak terlihat

### Expectations
- Improves: visibilitas dan kontrol
- Does not guarantee: growth langsung

## How

### Step-by-step method
1. Pilih 5 event paling penting.
2. Tulis tujuan tiap event.
3. Tambahkan contoh kapan event terjadi.
4. Pilih 2 metrik dasar.
5. Pasang alert untuk lonjakan error.

### Do and don't

**Do**
- Catat event yang berdampak pada produk
- Gunakan nama event yang jelas

**Don't**
- Mencatat semua hal tanpa filter
- Mengabaikan metrik dasar

### Common mistakes and fixes
- **Mistake:** Terlalu banyak event. **Fix:** Fokus pada yang paling penting.
- **Mistake:** Tidak ada metrik dasar. **Fix:** Pilih 2 metrik sederhana.

### Done when
- [ ] 5 event ditulis dengan tujuan.
- [ ] 2 metrik dasar ditetapkan.
- [ ] Alert dipasang.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar fitur
- Event penting

### Steps
1. Pilih 5 event.
2. Tulis tujuan dan contoh.
3. Pilih 2 metrik dasar.

### Output format
| Field | Value |
|---|---|
| Event | |
| Purpose | |
| Example | |
| Metric | |

> **Pro tip:** Catat event “request failed” untuk pemantauan error.

## Independent exercise (5 to 10 min)

### Task
Kurangi event menjadi 3 jika terlalu banyak dan jelaskan alasannya.

### Output
Daftar event baru dan alasan.

## Self-check (yes/no)

- [ ] Apakah event penting dicatat?
- [ ] Apakah metrik dasar ditentukan?
- [ ] Apakah contoh event ada?
- [ ] Apakah alert dipasang?

### Baseline metric (recommended)
- **Score:** 4 dari 5 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Product Analytics Basics**. Amplitude. 2024-01-01.
   Read: https://amplitude.com/blog/product-analytics

2. **Logging Best Practices**. Google. 2024-01-01.
   Read: https://cloud.google.com/logging/docs

## Read more (optional)

1. **Event Design Guide**
   Why: Panduan mendesain event yang bermakna.
   Read: https://amplitude.com/blog
