# Lesson 24: Integrasi Stripe checkout

**One-liner:** Siapkan Stripe checkout untuk menerima pembayaran dengan aman.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Flow Stripe Checkout

## Learning goal

You will be able to: **Mengintegrasikan Stripe checkout flow yang berfungsi.**

### Success criteria (observable)
- [ ] Checkout session dibuat dengan harga yang benar.
- [ ] Pengguna menyelesaikan pembayaran dan kembali ke app.
- [ ] Status pembayaran terlihat.

### Output you will produce
- **Deliverable:** Flow Stripe Checkout
- **Format:** Langkah flow dan test log
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menyiapkan pembayaran
**Secondary persona(s):** Pelanggan berbayar
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Integrasi Stripe checkout yang memungkinkan pengguna membayar lalu kembali ke app.
Flow ini aman dan cepat untuk produk awal.

### What it is not
Bukan sistem billing enterprise.
Bukan membangun UI pembayaran dari nol.

### 2-minute theory
- Stripe checkout mengurangi beban compliance.
- Flow sederhana mengurangi drop off pembayaran.
- Test mode memungkinkan uji tanpa risiko.

### Key terms
- **Checkout session:** Sesi pembayaran dari Stripe.
- **Success URL:** URL kembali setelah pembayaran sukses.

## Where

### Applies in
- Backend payment routes
- Checkout page

### Does not apply in
- Produk tanpa pembayaran

### Touchpoints
- Stripe dashboard
- Webhook logs
- Success page

## When

### Use it when
- Siap menagih pembayaran
- Butuh flow pembayaran cepat

### Frequency
Setiap menambah produk baru

### Late signals
- Checkout kembali tanpa status
- Pembayaran gagal tanpa alasan

## Why it matters

### Practical benefits
- Pembayaran lebih mudah
- Compliance lebih ringan
- Kepercayaan pelanggan meningkat

### Risks of ignoring
- Pembayaran macet
- UX buruk

### Expectations
- Improves: kemampuan menagih
- Does not guarantee: conversion tinggi

## How

### Step-by-step method
1. Buat product dan price di Stripe.
2. Buat checkout session di server.
3. Atur success URL dan cancel URL.
4. Uji dengan test mode.
5. Verifikasi status pembayaran di app.

### Do and don't

**Do**
- Gunakan test mode lebih dulu
- Verifikasi status di server

**Don't**
- Percaya status dari client
- Menyimpan success URL tanpa pengamanan

### Common mistakes and fixes
- **Mistake:** Success URL salah. **Fix:** Periksa routing dan URL.
- **Mistake:** Harga tidak tepat. **Fix:** Validasi price id.

### Done when
- [ ] Checkout flow berjalan di test mode.
- [ ] Success page menampilkan status.
- [ ] Pengguna kembali tanpa error.

## Guided exercise (10 to 15 min)

### Inputs
- Stripe account
- Price id

### Steps
1. Buat product dan price.
2. Buat checkout session.
3. Uji pembayaran di test mode.

### Output format
| Field | Value |
|---|---|
| Product name | |
| Price id | |
| Success URL | |
| Test result | |

> **Pro tip:** Gunakan Stripe test card untuk uji.

## Independent exercise (5 to 10 min)

### Task
Ubah harga dan uji kembali.

### Output
Price id baru dan hasil uji.

## Self-check (yes/no)

- [ ] Apakah checkout session dibuat?
- [ ] Apakah success URL berfungsi?
- [ ] Apakah status pembayaran diverifikasi?
- [ ] Apakah test mode berhasil?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Stripe Checkout Guide**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/checkout

2. **Payment Security Basics**. PCI SSC. 2024-01-01.
   Read: https://www.pcisecuritystandards.org/

## Read more (optional)

1. **Stripe Testing**
   Why: Uji sebelum production.
   Read: https://stripe.com/docs/testing
