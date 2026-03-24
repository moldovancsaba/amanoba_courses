# Lesson 9: Struktur proyek dan konfigurasi environment

**One-liner:** Susun struktur proyek dan env agar rapi dan aman.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Struktur Proyek dan Env Map

## Learning goal

You will be able to: **Membuat struktur proyek dan konfigurasi environment yang jelas.**

### Success criteria (observable)
- [ ] Struktur folder utama jelas dan konsisten.
- [ ] Env variables utama terdaftar.
- [ ] Ada pemisahan antara development dan production.

### Output you will produce
- **Deliverable:** Struktur Proyek dan Env Map
- **Format:** Daftar folder dan tabel env
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menyiapkan struktur proyek
**Secondary persona(s):** Kolaborator atau reviewer
**Stakeholders (optional):** Mitra proyek

## What

### What it is
Struktur proyek yang jelas dan daftar env variables penting.
Ini membuat proyek mudah dipahami dan aman.

### What it is not
Bukan arsitektur enterprise.
Bukan deployment penuh.

### 2-minute theory
- Struktur jelas mengurangi waktu onboarding.
- Env map mencegah kebocoran secrets.
- Pemisahan dev dan production mengurangi risiko.

### Key terms
- **Env map:** Daftar env variables dan kegunaannya.
- **Config:** Pengaturan yang membedakan lingkungan.

## Where

### Applies in
- Repo proyek
- Setup environment

### Does not apply in
- Dokumentasi pemasaran

### Touchpoints
- Folder structure
- .env files
- Deployment settings

## When

### Use it when
- Setelah setup repo
- Sebelum build fitur utama

### Frequency
Sekali di awal, revisi saat bertambah fitur

### Late signals
- Secrets tercampur di code
- Bingung variabel mana dipakai di production

## Why it matters

### Practical benefits
- Setup lebih cepat
- Risiko kebocoran menurun
- Kolaborasi lebih mudah

### Risks of ignoring
- Konfigurasi kacau
- Deploy gagal karena env hilang

### Expectations
- Improves: keteraturan dan keamanan
- Does not guarantee: bebas bug

## How

### Step-by-step method
1. Buat folder utama: app, server, docs.
2. Catat env variables utama.
3. Buat contoh file .env.example.
4. Pisahkan dev dan production config.
5. Dokumentasikan di README.

### Do and don't

**Do**
- Buat .env.example
- Pisahkan config dev dan production

**Don't**
- Menaruh secrets di code
- Membiarkan env variables tanpa dokumentasi

### Common mistakes and fixes
- **Mistake:** Tidak ada .env.example. **Fix:** Tambahkan contoh.
- **Mistake:** Tidak ada pemisahan env. **Fix:** Buat config terpisah.

### Done when
- [ ] Struktur proyek jelas.
- [ ] Env map tersedia.
- [ ] Dev dan production dibedakan.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar fitur utama
- Env variables yang dibutuhkan

### Steps
1. Tulis struktur folder.
2. Daftarkan env variables.
3. Buat .env.example.

### Output format
| Section | Item | Purpose |
|---|---|---|
| Folder | | |
| Env variable | | |

> **Pro tip:** Simpan env map di README agar mudah ditemukan.

## Independent exercise (5 to 10 min)

### Task
Tambahkan satu env variable baru dan dokumentasikan.

### Output
Env map yang diperbarui.

## Self-check (yes/no)

- [ ] Apakah struktur proyek jelas?
- [ ] Apakah env variables terdokumentasi?
- [ ] Apakah .env.example ada?
- [ ] Apakah dev dan production dipisahkan?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Configuration Best Practices**. 12 Factor. 2024-01-01.
   Read: https://12factor.net/config

2. **Env Management**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs/projects/environment-variables

## Read more (optional)

1. **Project Structure Guide**
   Why: Struktur yang rapi mempercepat tim.
   Read: https://12factor.net/
