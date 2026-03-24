# Lesson 13: Desain workflow agent

**One-liner:** Rancang langkah agent yang jelas, kecil, dan bisa diuji.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Peta Workflow Agent dan Langkah

## Learning goal

You will be able to: **Mendesain workflow agent dengan langkah jelas dan kriteria keberhasilan.**

### Success criteria (observable)
- [ ] Workflow memiliki minimal 4 langkah berurutan.
- [ ] Setiap langkah punya input dan output.
- [ ] Ada setidaknya satu guardrail atau verifikasi.

### Output you will produce
- **Deliverable:** Peta Workflow Agent dan Langkah
- **Format:** Daftar langkah dan diagram sederhana
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang merancang workflow agent
**Secondary persona(s):** Pengguna yang mengandalkan hasil akurat
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Susunan langkah kecil yang diikuti agent untuk menghasilkan output.
Ini memberi kejelasan tentang input, output, dan keputusan.

### What it is not
Bukan alur panjang tanpa batas.
Bukan pengganti logika produk atau approval.

### 2-minute theory
- Workflow yang jelas mengurangi error dan kerja ulang.
- Langkah kecil membuat agent lebih mudah diuji.
- Guardrails mencegah hasil berbahaya.

### Key terms
- **Workflow:** Urutan langkah menuju hasil.
- **Guardrail:** Aturan untuk mencegah tindakan berisiko.

## Where

### Applies in
- Orkestrasi agent
- Backend flows

### Does not apply in
- Task tunggal yang selesai dengan satu prompt

### Touchpoints
- Flow diagram
- Step logs
- Test scenarios

## When

### Use it when
- Agent memiliki beberapa langkah
- Anda butuh troubleshooting yang jelas

### Frequency
Setiap membuat agent baru

### Late signals
- Agent melewatkan langkah penting
- Output sulit dipahami

## Why it matters

### Practical benefits
- Output lebih stabil
- Debugging lebih cepat
- Keamanan action lebih baik

### Risks of ignoring
- Workflow tidak jelas
- Output tidak konsisten

### Expectations
- Improves: kejelasan dan keandalan
- Does not guarantee: hasil sempurna

## How

### Step-by-step method
1. Definisikan tujuan akhir agent.
2. Pecah menjadi 4 sampai 6 langkah.
3. Tentukan input dan output setiap langkah.
4. Tambahkan guardrail atau verifikasi.
5. Catat aliran data antar langkah.

### Do and don't

**Do**
- Buat langkah pendek dan jelas
- Log langkah penting

**Don't**
- Menggabungkan banyak task dalam satu langkah
- Melewatkan verifikasi

### Common mistakes and fixes
- **Mistake:** Langkah terlalu besar. **Fix:** Pecah menjadi dua.
- **Mistake:** Tidak ada verifikasi. **Fix:** Tambahkan check kualitas.

### Done when
- [ ] Semua langkah punya input dan output.
- [ ] Ada minimal satu guardrail.
- [ ] Workflow terdokumentasi.

## Guided exercise (10 to 15 min)

### Inputs
- Tujuan agent
- Output yang diinginkan

### Steps
1. Tulis 5 langkah workflow.
2. Jelaskan input dan output tiap langkah.
3. Tambahkan guardrail di satu langkah.

### Output format
| Field | Value |
|---|---|
| Step list | |
| Inputs | |
| Outputs | |
| Guardrail | |

> **Pro tip:** Mulai dengan langkah memahami masalah sebelum menghasilkan output.

## Independent exercise (5 to 10 min)

### Task
Hapus satu langkah dan cek apakah workflow masih jelas.

### Output
Workflow yang disederhanakan dan alasan.

## Self-check (yes/no)

- [ ] Apakah langkah berurutan jelas?
- [ ] Apakah input dan output dijelaskan?
- [ ] Apakah ada guardrail?
- [ ] Apakah workflow mudah diikuti?

### Baseline metric (recommended)
- **Score:** 4 dari 5 langkah jelas
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Agent Design Patterns**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs

2. **Workflow Automation Basics**. Zapier. 2024-01-01.
   Read: https://zapier.com/learn/automation/what-are-workflows/

## Read more (optional)

1. **Agent Orchestration Guide**
   Why: Pola orkestrasi agent.
   Read: https://platform.openai.com/docs
