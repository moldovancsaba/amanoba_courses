# Lesson 25: Stripe webhooks dan kontrol akses

**One-liner:** Gunakan webhooks untuk memverifikasi pembayaran dan kontrol akses.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Flow Webhook dan Aturan Akses

## Learning goal

You will be able to: **Mengatur webhook Stripe dan aturan akses untuk pelanggan berbayar.**

### Success criteria (observable)
- [ ] Webhook memverifikasi signature.
- [ ] Status pembayaran memengaruhi akses.
- [ ] Test event berhasil.

### Output you will produce
- **Deliverable:** Flow Webhook dan Aturan Akses
- **Format:** Diagram flow dan rules
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang memastikan pembayaran dan akses
**Secondary persona(s):** Pelanggan berbayar
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Webhook menerima event Stripe dan memvalidasi status pembayaran.
Aturan akses menentukan siapa yang bisa menggunakan fitur.

### What it is not
Bukan sistem billing lengkap.
Bukan kontrol akses enterprise.

### 2-minute theory
- Webhook adalah sumber kebenaran untuk status pembayaran.
- Verifikasi signature mencegah event palsu.
- Kontrol akses mencegah penyalahgunaan produk.

### Key terms
- **Webhook:** Endpoint yang menerima event dari layanan eksternal.
- **Signature verification:** Verifikasi bahwa event sah.

## Where

### Applies in
- Backend routes
- Access middleware

### Does not apply in
- Produk gratis tanpa pembayaran

### Touchpoints
- Stripe dashboard
- Webhook logs
- Access checks

## When

### Use it when
- Anda mulai menagih pembayaran
- Anda perlu kontrol akses

### Frequency
Setiap menambah plan baru

### Late signals
- Pengguna tidak berbayar mendapat akses
- Akses hilang setelah pembayaran

## Why it matters

### Practical benefits
- Akses tepat untuk pelanggan berbayar
- Mengurangi kecurangan
- Kepercayaan sistem meningkat

### Risks of ignoring
- Kehilangan pendapatan
- Pengalaman pengguna buruk

### Expectations
- Improves: kontrol dan kepercayaan
- Does not guarantee: nol kecurangan

## How

### Step-by-step method
1. Buat webhook endpoint di server.
2. Simpan signing secret di env.
3. Verifikasi signature event.
4. Update status pembayaran di database.
5. Gunakan status untuk kontrol akses.

### Do and don't

**Do**
- Validasi signature untuk setiap event
- Log event penting

**Don't**
- Percaya status dari client
- Membiarkan webhook tanpa retry

### Common mistakes and fixes
- **Mistake:** Signature tidak diverifikasi. **Fix:** Gunakan signing secret.
- **Mistake:** Status tidak diupdate. **Fix:** Update dari webhook.

### Done when
- [ ] Webhook endpoint berjalan.
- [ ] Signature verification berhasil.
- [ ] Akses sesuai status.

## Guided exercise (10 to 15 min)

### Inputs
- Stripe signing secret
- Daftar event penting

### Steps
1. Siapkan webhook endpoint.
2. Verifikasi signature.
3. Jalankan test event dan catat hasil.

### Output format
| Field | Value |
|---|---|
| Webhook URL | |
| Event type | |
| Signature status | |
| Access change | |

> **Pro tip:** Tambahkan retry logic untuk event yang gagal.

## Independent exercise (5 to 10 min)

### Task
Tambahkan event baru dan jelaskan pengaruhnya terhadap akses.

### Output
Event baru dan aturan aksesnya.

## Self-check (yes/no)

- [ ] Apakah webhook memverifikasi signature?
- [ ] Apakah status pembayaran diperbarui?
- [ ] Apakah akses sesuai status?
- [ ] Apakah test event berhasil?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Stripe Webhooks**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/webhooks

2. **Webhook Security**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/webhooks/signatures

## Read more (optional)

1. **Access Control Basics**
   Why: Dasar kontrol akses.
   Read: https://owasp.org/
