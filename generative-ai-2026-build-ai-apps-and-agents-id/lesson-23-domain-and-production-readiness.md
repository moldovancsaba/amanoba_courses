# Lesson 23: Domain dan kesiapan production

**One-liner:** Siapkan domain dan pastikan app siap untuk production.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Checklist Kesiapan Production

## Learning goal

You will be able to: **Menghubungkan domain dan memverifikasi kesiapan production.**

### Success criteria (observable)
- [ ] Domain terhubung dan SSL aktif.
- [ ] Health check lulus.
- [ ] Checklist kesiapan lengkap.

### Output you will produce
- **Deliverable:** Checklist Kesiapan Production
- **Format:** Daftar periksa
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menyiapkan app untuk production
**Secondary persona(s):** Pengguna awal
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Langkah menghubungkan domain dan memastikan app siap dipakai.
Mencakup SSL, health check, dan pemeriksaan akhir.

### What it is not
Bukan rencana SRE penuh.
Bukan monitoring tingkat enterprise.

### 2-minute theory
- Domain resmi meningkatkan kepercayaan.
- SSL melindungi data saat transit.
- Checklist mengurangi kesalahan di menit akhir.

### Key terms
- **SSL:** Perlindungan data saat transit.
- **Health check:** Uji cepat status app.

## Where

### Applies in
- Domain provider
- Vercel settings

### Does not apply in
- App internal tanpa akses publik

### Touchpoints
- DNS records
- SSL status
- Health endpoint

## When

### Use it when
- Anda siap launch
- Ingin domain resmi

### Frequency
Setiap launch besar

### Late signals
- SSL tidak aktif
- Health check gagal

## Why it matters

### Practical benefits
- Kepercayaan pengguna meningkat
- Data terlindungi
- Launch lebih lancar

### Risks of ignoring
- Peringatan browser
- Kepercayaan turun

### Expectations
- Improves: keamanan dan kepercayaan
- Does not guarantee: uptime 100 persen

## How

### Step-by-step method
1. Gunakan domain yang Anda miliki.
2. Atur DNS ke Vercel.
3. Verifikasi SSL aktif.
4. Jalankan health check.
5. Lengkapi checklist kesiapan.

### Do and don't

**Do**
- Pilih domain yang mudah diingat
- Pastikan SSL aktif

**Don't**
- Launch tanpa health check
- Biarkan DNS tanpa verifikasi

### Common mistakes and fixes
- **Mistake:** DNS salah. **Fix:** Periksa record dan subdomain.
- **Mistake:** SSL belum aktif. **Fix:** Selesaikan verifikasi domain.

### Done when
- [ ] Domain menampilkan app.
- [ ] SSL aktif.
- [ ] Health check lulus.

## Guided exercise (10 to 15 min)

### Inputs
- Domain yang dimiliki
- Project Vercel

### Steps
1. Atur DNS records.
2. Verifikasi SSL.
3. Jalankan health check.

### Output format
| Field | Value |
|---|---|
| Domain | |
| SSL status | |
| Health check | |
| Notes | |

> **Pro tip:** Gunakan subdomain untuk staging.

## Independent exercise (5 to 10 min)

### Task
Tambahkan endpoint health check pada app.

### Output
URL health check dan hasil.

## Self-check (yes/no)

- [ ] Apakah domain menampilkan app?
- [ ] Apakah SSL aktif?
- [ ] Apakah health check lulus?
- [ ] Apakah checklist lengkap?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Vercel Domains**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs

2. **SSL Basics**. Cloudflare. 2024-01-01.
   Read: https://www.cloudflare.com/learning/ssl/what-is-ssl/

## Read more (optional)

1. **Production Readiness Checklist**
   Why: Pemeriksaan akhir sebelum launch.
   Read: https://vercel.com/docs
