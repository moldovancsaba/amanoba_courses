# Lesson 15: Kontrol biaya dan rate limits

**One-liner:** Tambahkan guardrails agar biaya AI tetap terprediksi.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Checklist Kontrol Biaya dan Batas

## Learning goal

You will be able to: **Menetapkan batas biaya dan rate limits untuk melindungi produk AI Anda.**

### Success criteria (observable)
- [ ] Checklist kontrol biaya lengkap.
- [ ] Rate limits ditetapkan untuk endpoint penting.
- [ ] Batas biaya bulanan ditulis.

### Output you will produce
- **Deliverable:** Checklist Kontrol Biaya dan Batas
- **Format:** Checklist dan tabel batas
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang mengelola biaya AI
**Secondary persona(s):** Pelanggan berbayar yang mengandalkan layanan stabil
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Sekumpulan aturan kecil untuk membatasi penggunaan dan melindungi budget.
Menggabungkan cost cap dan rate limits agar satu pengguna tidak menghabiskan biaya.

### What it is not
Bukan sistem keuangan lengkap.
Bukan pengganti strategi harga.

### 2-minute theory
- Biaya AI bisa naik cepat dengan penggunaan berat.
- Rate limits melindungi stabilitas dan anggaran.
- Cost cap membuat eksperimen harga lebih aman.

### Key terms
- **Rate limit:** Aturan yang membatasi request per pengguna atau waktu.
- **Cost cap:** Batas biaya maksimal per periode.

## Where

### Applies in
- API routes
- Billing logic

### Does not apply in
- Uji manual sekali pakai

### Touchpoints
- Usage logs
- Billing dashboard
- Alert rules

## When

### Use it when
- App dibuka untuk pengguna nyata
- Anda mulai menagih pembayaran

### Frequency
Tetapkan sekali, revisi saat penggunaan bertambah

### Late signals
- Lonjakan penggunaan tidak wajar
- Tagihan lebih besar dari perkiraan

## Why it matters

### Practical benefits
- Biaya lebih terprediksi
- Lebih sedikit outage
- Kontrol pemakaian gratis lebih baik

### Risks of ignoring
- Tagihan mengejutkan
- Penyalahgunaan oleh heavy users

### Expectations
- Improves: stabilitas biaya dan keamanan
- Does not guarantee: margin sempurna

## How

### Step-by-step method
1. Pilih cost cap bulanan.
2. Tetapkan rate limits per pengguna.
3. Tambahkan batas harian untuk pengguna gratis.
4. Pasang alert untuk lonjakan.
5. Tinjau usage tiap minggu.

### Do and don't

**Do**
- Mulai dengan batas konservatif
- Catat usage per pengguna

**Don't**
- Memberi penggunaan gratis tanpa kontrol
- Menunggu tagihan baru bertindak

### Common mistakes and fixes
- **Mistake:** Tidak ada cost cap. **Fix:** Tetapkan cost cap kecil.
- **Mistake:** Tidak ada batas per pengguna. **Fix:** Tambahkan rate limits.

### Done when
- [ ] Cost cap bulanan ditulis.
- [ ] Rate limits ditetapkan.
- [ ] Alert terpasang.

## Guided exercise (10 to 15 min)

### Inputs
- Perkiraan usage per pengguna
- Hipotesis harga saat ini

### Steps
1. Estimasikan biaya per request.
2. Tetapkan anggaran bulanan.
3. Tentukan batas per pengguna.

### Output format
| Field | Value |
|---|---|
| Cost per request | |
| Monthly cap | |
| Rate limits | |
| Alert trigger | |

> **Pro tip:** Mulai dengan cap kecil lalu tingkatkan setelah ada data nyata.

## Independent exercise (5 to 10 min)

### Task
Buat aturan untuk heavy user dan jelaskan tindakan.

### Output
Aturan heavy user dan responsnya.

## Self-check (yes/no)

- [ ] Apakah cost cap bulanan ditetapkan?
- [ ] Apakah batas per pengguna ditetapkan?
- [ ] Apakah alert terpasang?
- [ ] Apakah usage ditinjau mingguan?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Pricing**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/pricing

2. **API Rate Limiting Guide**. Cloudflare. 2024-01-01.
   Read: https://developers.cloudflare.com/rate-limits/

## Read more (optional)

1. **Usage Based Pricing**
   Why: Menyelaraskan biaya dengan paket harga.
   Read: https://www.profitwell.com/recur/all/usage-based-pricing
