# Lesson 11: Desain prompt untuk keandalan

**One-liner:** Rancang prompt yang menghasilkan output stabil dan bisa diuji.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Spesifikasi Prompt dan Set Uji

## Learning goal

You will be able to: **Menulis spesifikasi prompt dan set uji kecil untuk meningkatkan keandalan.**

### Success criteria (observable)
- [ ] Prompt mencakup role, task, dan format output.
- [ ] Set uji memiliki minimal 5 input representatif.
- [ ] Minimal 4 dari 5 uji memenuhi output yang diharapkan.

### Output you will produce
- **Deliverable:** Spesifikasi Prompt dan Set Uji
- **Format:** Dokumen prompt dan tabel uji
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang merancang prompt untuk app AI komersial
**Secondary persona(s):** Pengguna yang menginginkan output konsisten
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Spesifikasi prompt yang jelas tentang apa yang harus dilakukan model dan format output.
Set uji kecil yang mengungkap kelemahan sebelum pengguna menemukannya.

### What it is not
Bukan prompt panjang yang mencoba menyelesaikan semua kasus.
Bukan pengganti logic produk atau validasi.

### 2-minute theory
- Prompt adalah interface produk yang harus andal.
- Struktur yang jelas mengurangi drift output.
- Set uji kecil menangkap error dengan effort rendah.

### Key terms
- **Prompt spec:** Instruksi terstruktur dengan role, task, dan format.
- **Test set:** Kumpulan input untuk memvalidasi kualitas output.

## Where

### Applies in
- System prompt
- Prompt khusus fitur

### Does not apply in
- Copy pemasaran atau konten UI

### Touchpoints
- File prompt
- Test cases
- Log output

## When

### Use it when
- Menambah fitur AI baru
- Output sering tidak konsisten

### Frequency
Setiap kali prompt diubah

### Late signals
- Output sering melanggar format
- Pengguna melapor hasil tidak konsisten

## Why it matters

### Practical benefits
- Output lebih konsisten
- Debugging lebih cepat
- Kepercayaan pengguna meningkat

### Risks of ignoring
- Output tidak dapat diprediksi
- Beban support meningkat

### Expectations
- Improves: keandalan dan kejelasan
- Does not guarantee: akurasi sempurna

## How

### Step-by-step method
1. Tulis role dan task dalam satu kalimat.
2. Definisikan format output dengan contoh singkat.
3. Tambahkan constraints seperti tone atau panjang.
4. Buat set uji 5 input.
5. Jalankan uji dan catat pass rate.

### Do and don't

**Do**
- Gunakan format output yang eksplisit
- Buat prompt singkat dan fokus

**Don't**
- Mencampur banyak task dalam satu prompt
- Melewati pengujian input nyata

### Common mistakes and fixes
- **Mistake:** Format tidak jelas. **Fix:** Tambahkan template output.
- **Mistake:** Tidak ada uji. **Fix:** Buat set uji kecil.

### Done when
- [ ] Prompt berisi role, task, dan format.
- [ ] Set uji berisi 5 input.
- [ ] Pass rate tercatat.

## Guided exercise (10 to 15 min)

### Inputs
- Deskripsi fitur Anda
- 5 input pengguna representatif

### Steps
1. Tulis spesifikasi prompt dengan role, task, dan format.
2. Tulis output yang diharapkan untuk tiap input.
3. Catat pass atau fail.

### Output format
| Field | Value |
|---|---|
| Prompt spec | |
| Input set | |
| Expected output | |
| Pass rate | |

> **Pro tip:** Gunakan input pengguna nyata, bukan contoh ideal saja.

## Independent exercise (5 to 10 min)

### Task
Pendekkan prompt 20 persen tanpa mengurangi kejelasan.

### Output
Spesifikasi prompt yang diperbarui dan hasil uji terbaru.

## Self-check (yes/no)

- [ ] Apakah prompt mendefinisikan role, task, dan format?
- [ ] Apakah input realistis dan bervariasi?
- [ ] Apakah pass rate tercatat?
- [ ] Apakah prompt mudah dibaca?

### Baseline metric (recommended)
- **Score:** 4 dari 5 uji lulus
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Prompt Engineering Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/prompt-engineering

2. **Prompting Best Practices**. Anthropic. 2026-02-06.
   Read: https://docs.anthropic.com/claude/docs/prompting

## Read more (optional)

1. **System Prompt Best Practices**
   Why: Pedoman output yang stabil.
   Read: https://platform.openai.com/docs/guides/prompt-engineering
