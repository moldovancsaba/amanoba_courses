# Lesson 21: Dasar keamanan dan privasi

**One-liner:** Lindungi data dan sistem dengan langkah keamanan yang praktis.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Checklist Keamanan dan Privasi

## Learning goal

You will be able to: **Menyusun checklist keamanan dan privasi untuk app AI komersial.**

### Success criteria (observable)
- [ ] Checklist memiliki minimal 8 item penting.
- [ ] Ada langkah untuk melindungi API key dan data pengguna.
- [ ] Ada langkah pertama untuk incident response.

### Output you will produce
- **Deliverable:** Checklist Keamanan dan Privasi
- **Format:** Daftar periksa dan catatan singkat
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menjalankan app AI untuk pengguna nyata
**Secondary persona(s):** Pengguna yang peduli keamanan
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Daftar langkah dasar untuk melindungi sistem, data, dan akses.
Membantu Anda memulai keamanan tanpa tim besar.

### What it is not
Bukan audit keamanan lengkap.
Bukan pengganti nasihat legal.

### 2-minute theory
- Langkah kecil mengurangi risiko besar di awal.
- Privasi meningkatkan kepercayaan dan mengurangi risiko legal.
- Checklist mencegah hal penting terlewat.

### Key terms
- **Least privilege:** Akses minimum yang diperlukan untuk setiap peran.
- **Incident response:** Langkah yang diambil saat terjadi insiden.

## Where

### Applies in
- Access control
- Data storage

### Does not apply in
- Demo internal tanpa data pengguna

### Touchpoints
- API keys
- Database
- Audit logs

## When

### Use it when
- Meluncurkan untuk pengguna pertama
- Mulai menyimpan data pengguna

### Frequency
Setiap rilis besar

### Late signals
- API key terlihat di repo
- Permintaan hapus data terlambat

## Why it matters

### Practical benefits
- Risiko kebocoran berkurang
- Kepercayaan pengguna meningkat
- Respon insiden lebih cepat

### Risks of ignoring
- Kebocoran data
- Kehilangan kepercayaan

### Expectations
- Improves: keamanan dasar
- Does not guarantee: perlindungan sempurna

## How

### Step-by-step method
1. Aktifkan MFA untuk akun penting.
2. Terapkan least privilege untuk tim.
3. Simpan API key di env variables.
4. Redaksi data sensitif di log.
5. Tetapkan retensi dan penghapusan data.
6. Tulis langkah pertama incident response.

### Do and don't

**Do**
- Gunakan secrets manager atau env variables
- Catat akses penting

**Don't**
- Menaruh key di client
- Menyimpan data sensitif di log

### Common mistakes and fixes
- **Mistake:** Tidak ada MFA. **Fix:** Aktifkan MFA untuk akun penting.
- **Mistake:** Log berisi data sensitif. **Fix:** Redaksi data sensitif.

### Done when
- [ ] Checklist berisi 8 item.
- [ ] API key terlindungi.
- [ ] Incident response langkah pertama ada.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar akun dan layanan
- Jenis data sensitif

### Steps
1. Buat checklist 8 item.
2. Tambahkan 2 item privasi.
3. Tulis langkah pertama incident response.

### Output format
| Field | Value |
|---|---|
| Security item | |
| Privacy item | |
| Owner | |
| Status | |

> **Pro tip:** Mulai dari MFA dan perlindungan API key.

## Independent exercise (5 to 10 min)

### Task
Tambahkan satu langkah audit keamanan sederhana.

### Output
Item baru pada checklist.

## Self-check (yes/no)

- [ ] Apakah MFA aktif?
- [ ] Apakah API key terlindungi?
- [ ] Apakah retensi data ditulis?
- [ ] Apakah incident response langkah pertama ada?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OWASP Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/

2. **NIST Privacy Framework**. NIST. 2024-01-01.
   Read: https://www.nist.gov/privacy-framework

## Read more (optional)

1. **Security Basics for Startups**
   Why: Langkah keamanan dasar.
   Read: https://owasp.org/
