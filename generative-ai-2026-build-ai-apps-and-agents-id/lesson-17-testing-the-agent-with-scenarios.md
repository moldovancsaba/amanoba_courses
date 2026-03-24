# Lesson 17: Pengujian agent dengan skenario

**One-liner:** Gunakan skenario nyata untuk menguji perilaku agent sebelum rilis.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Set Skenario Uji Agent

## Learning goal

You will be able to: **Membuat skenario uji dan mengevaluasi output agent.**

### Success criteria (observable)
- [ ] Set berisi minimal 5 skenario nyata.
- [ ] Setiap skenario memiliki input dan output yang diharapkan.
- [ ] Setidaknya satu skenario adalah edge case.

### Output you will produce
- **Deliverable:** Set Skenario Uji Agent
- **Format:** Tabel skenario dan hasil
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menguji agent sebelum rilis
**Secondary persona(s):** Pengguna yang mengandalkan hasil konsisten
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Kumpulan skenario yang mewakili penggunaan nyata.
Setiap skenario memiliki input, output diharapkan, dan hasil pass atau fail.

### What it is not
Bukan unit test teknis saja.
Bukan input acak tanpa konteks.

### 2-minute theory
- Skenario nyata mengungkap kelemahan lebih cepat.
- Edge case menguji batas kemampuan agent.
- Hasil uji yang dicatat memperkuat QA.

### Key terms
- **Scenario:** Situasi penggunaan dengan konteks dan tujuan.
- **Edge case:** Kasus jarang yang dapat memecahkan sistem.

## Where

### Applies in
- QA agent
- Uji sebelum launch

### Does not apply in
- Demo tanpa pengguna nyata

### Touchpoints
- Daftar skenario
- Test log
- Backlog bug

## When

### Use it when
- Mendekati launch
- Mengubah workflow agent

### Frequency
Setiap perubahan besar

### Late signals
- Pengguna melapor error tanpa pola
- Agent gagal di edge case

## Why it matters

### Practical benefits
- Lebih sedikit error pasca launch
- Pemahaman batas agent lebih baik
- Kepercayaan pengguna meningkat

### Risks of ignoring
- Bug di production
- Tiket support meningkat

### Expectations
- Improves: keandalan dan kepercayaan
- Does not guarantee: bebas bug

## How

### Step-by-step method
1. Daftarkan 5 penggunaan paling umum.
2. Tambahkan 1 edge case penting.
3. Tulis input dan output yang diharapkan.
4. Jalankan uji dan catat hasil.
5. Buat tiket untuk error penting.

### Do and don't

**Do**
- Gunakan data contoh yang realistis
- Catat pass atau fail

**Don't**
- Menulis skenario tanpa konteks
- Mengabaikan edge case

### Common mistakes and fixes
- **Mistake:** Skenario terlalu umum. **Fix:** Tambahkan konteks pengguna.
- **Mistake:** Tidak ada edge case. **Fix:** Tambahkan satu skenario ekstrem.

### Done when
- [ ] Ada 5 skenario tertulis.
- [ ] Output diharapkan ditulis.
- [ ] Hasil uji dicatat.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar penggunaan utama
- Persona pengguna

### Steps
1. Tulis 5 skenario.
2. Tuliskan output yang diharapkan.
3. Catat hasil uji.

### Output format
| Field | Value |
|---|---|
| Scenario | |
| Input | |
| Expected output | |
| Pass or fail | |

> **Pro tip:** Buat satu skenario dengan data kotor untuk menguji batas.

## Independent exercise (5 to 10 min)

### Task
Tambahkan satu skenario risiko tinggi dan uji.

### Output
Skenario baru dan hasilnya.

## Self-check (yes/no)

- [ ] Apakah skenario realistis?
- [ ] Apakah ada edge case?
- [ ] Apakah hasil uji dicatat?
- [ ] Apakah bug penting ditulis?

### Baseline metric (recommended)
- **Score:** 5 dari 6 skenario lulus
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Testing AI Systems**. Microsoft. 2024-01-01.
   Read: https://learn.microsoft.com/

2. **Scenario Based Testing**. Atlassian. 2024-01-01.
   Read: https://www.atlassian.com/continuous-delivery/software-testing/scenario-testing

## Read more (optional)

1. **Quality Assurance Basics**
   Why: Dasar QA yang sederhana.
   Read: https://www.atlassian.com/continuous-delivery/software-testing
