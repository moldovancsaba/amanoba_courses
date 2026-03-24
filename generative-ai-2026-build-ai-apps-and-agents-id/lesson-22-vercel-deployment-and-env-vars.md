# Lesson 22: Deployment Vercel dan env variables

**One-liner:** Deploy app ke Vercel dan atur env variables dengan aman.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Checklist Deployment Vercel dan Env Map

## Learning goal

You will be able to: **Melakukan deployment Vercel dan menyiapkan env variables yang aman.**

### Success criteria (observable)
- [ ] App berhasil deploy ke production di Vercel.
- [ ] Env variables penting sudah diset.
- [ ] Tidak ada error terkait secrets.

### Output you will produce
- **Deliverable:** Checklist Deployment Vercel dan Env Map
- **Format:** Checklist dan tabel env
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang melakukan deployment app AI
**Secondary persona(s):** Pengguna awal yang mengakses app
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Proses deploy app ke Vercel dan mengatur env variables.
Memastikan app dapat berjalan di production dengan aman.

### What it is not
Bukan migrasi database besar.
Bukan pipeline CI/CD enterprise.

### 2-minute theory
- Deployment yang stabil mengurangi downtime.
- Env variables melindungi secrets.
- Checklist memastikan langkah penting tidak terlewat.

### Key terms
- **Deployment:** Proses menempatkan app di server produksi.
- **Env variables:** Variabel lingkungan yang menyimpan secrets.

## Where

### Applies in
- Vercel dashboard
- Project settings

### Does not apply in
- App tanpa backend

### Touchpoints
- Build logs
- Env settings
- Deployment URL

## When

### Use it when
- App siap ditunjukkan ke pengguna
- Anda butuh URL production

### Frequency
Setiap rilis baru

### Late signals
- Build gagal karena env belum diatur
- API key terlihat di client

## Why it matters

### Practical benefits
- App dapat diakses pengguna
- Secrets tetap aman
- Deploy dapat diulang dengan cepat

### Risks of ignoring
- Build failures
- Kebocoran secrets

### Expectations
- Improves: stabilitas deployment
- Does not guarantee: performa maksimal

## How

### Step-by-step method
1. Hubungkan repo ke Vercel.
2. Atur env variables di Vercel.
3. Deploy ke production.
4. Periksa build logs.
5. Uji endpoint penting.

### Do and don't

**Do**
- Simpan secrets di env variables
- Periksa logs setelah deploy

**Don't**
- Menaruh secrets di code
- Mengabaikan build logs

### Common mistakes and fixes
- **Mistake:** Env variables belum diset. **Fix:** Isi di Vercel settings.
- **Mistake:** API key di client. **Fix:** Pindahkan ke server.

### Done when
- [ ] Deploy production berhasil.
- [ ] Env variables diset.
- [ ] App merespons di URL production.

## Guided exercise (10 to 15 min)

### Inputs
- Repo app
- Daftar env variables

### Steps
1. Hubungkan repo ke Vercel.
2. Isi env variables.
3. Deploy dan uji URL.

### Output format
| Field | Value |
|---|---|
| Vercel project | |
| Env variables set | |
| Deployment URL | |
| Test result | |

> **Pro tip:** Pisahkan env untuk staging dan production.

## Independent exercise (5 to 10 min)

### Task
Tambahkan satu env variable test dan pastikan terbaca.

### Output
Env map yang diperbarui.

## Self-check (yes/no)

- [ ] Apakah repo terhubung ke Vercel?
- [ ] Apakah env variables diset?
- [ ] Apakah build logs bersih?
- [ ] Apakah URL production aktif?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Vercel Deployment Guide**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs

2. **Env Variables Best Practices**. GitHub. 2024-01-01.
   Read: https://docs.github.com/en/actions/security-guides/encrypted-secrets

## Read more (optional)

1. **Vercel Environment Variables**
   Why: Pengaturan env di Vercel.
   Read: https://vercel.com/docs/projects/environment-variables
