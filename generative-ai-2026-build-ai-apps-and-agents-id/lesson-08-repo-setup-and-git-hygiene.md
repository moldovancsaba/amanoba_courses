# Lesson 8: Setup repo dan kebersihan Git

**One-liner:** Siapkan repo yang rapi agar kerja tim dan deployment lebih aman.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Repo Setup Checklist

## Learning goal

You will be able to: **Menyiapkan repo Git yang rapi dengan praktik kebersihan dasar.**

### Success criteria (observable)
- [ ] Repo punya struktur folder yang jelas.
- [ ] File penting seperti README dan .gitignore ada.
- [ ] Ada konvensi commit sederhana.

### Output you will produce
- **Deliverable:** Repo Setup Checklist
- **Format:** Checklist dan catatan struktur
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang menyiapkan repo
**Secondary persona(s):** Kolaborator atau reviewer
**Stakeholders (optional):** Mitra proyek

## What

### What it is
Pengaturan repo dasar agar proyek mudah dipahami dan aman.
Kebersihan Git memastikan perubahan terkontrol dan mudah dilacak.

### What it is not
Bukan proses CI/CD lengkap.
Bukan aturan Git tingkat enterprise.

### 2-minute theory
- Repo rapi memudahkan kolaborasi.
- README membantu onboarding cepat.
- .gitignore mencegah file sensitif masuk repo.

### Key terms
- **.gitignore:** Daftar file yang tidak boleh masuk Git.
- **Commit hygiene:** Kebiasaan membuat commit jelas dan kecil.

## Where

### Applies in
- Repo proyek
- Kolaborasi tim

### Does not apply in
- Dokumen pribadi di luar repo

### Touchpoints
- README
- Folder structure
- Commit history

## When

### Use it when
- Memulai proyek baru
- Mengundang kolaborator

### Frequency
Sekali di awal, revisi saat proyek berkembang

### Late signals
- Repo berantakan
- File sensitif tidak sengaja tercommit

## Why it matters

### Practical benefits
- Kolaborasi lebih cepat
- Risiko kebocoran berkurang
- Review lebih mudah

### Risks of ignoring
- Kesalahan deployment
- Histori commit sulit dibaca

### Expectations
- Improves: keteraturan dan keamanan
- Does not guarantee: bebas bug

## How

### Step-by-step method
1. Buat struktur folder yang jelas.
2. Tulis README singkat.
3. Tambahkan .gitignore.
4. Tetapkan aturan commit sederhana.
5. Buat commit awal yang bersih.

### Do and don't

**Do**
- Gunakan commit kecil dan jelas
- Simpan konfigurasi sensitif di env

**Don't**
- Commit file rahasia
- Menunda README

### Common mistakes and fixes
- **Mistake:** Tidak ada .gitignore. **Fix:** Tambahkan file .gitignore.
- **Mistake:** Commit terlalu besar. **Fix:** Pecah menjadi commit kecil.

### Done when
- [ ] Struktur repo rapi.
- [ ] README dan .gitignore ada.
- [ ] Commit awal sudah dibuat.

## Guided exercise (10 to 15 min)

### Inputs
- Daftar file proyek
- Template README

### Steps
1. Susun folder utama.
2. Tulis README satu halaman.
3. Buat .gitignore.

### Output format
| Field | Value |
|---|---|
| Folder structure | |
| README status | |
| .gitignore status | |
| Commit message | |

> **Pro tip:** Gunakan template README untuk konsistensi.

## Independent exercise (5 to 10 min)

### Task
Perbaiki satu commit besar menjadi dua commit kecil.

### Output
Dua commit dengan pesan jelas.

## Self-check (yes/no)

- [ ] Apakah struktur folder jelas?
- [ ] Apakah README ada?
- [ ] Apakah .gitignore ada?
- [ ] Apakah commit rapi?

### Baseline metric (recommended)
- **Score:** 3 dari 4 terpenuhi
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Git Best Practices**. Git SCM. 2024-01-01.
   Read: https://git-scm.com/book/en/v2

2. **README Guide**. GitHub. 2024-01-01.
   Read: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes

## Read more (optional)

1. **Git Commit Hygiene**
   Why: Membuat histori commit mudah dipahami.
   Read: https://git-scm.com/book/en/v2
