# Lesson 11 Quiz Pool

**Question:** Spesifikasi prompt mana yang paling andal untuk app AI komersial?

A) “Tolong tulis sesuatu tentang proposal.”
B) “Anda adalah asisten proposal. Buat ringkasan 6 poin dalam format: Title, Client, Goal, Constraints, Steps, Next action.”
C) “Gunakan AI untuk membantu pekerjaan.”
D) “Buat lebih baik untuk rilis pertama.”

**Correct:** B

**Why correct:** Memiliki role, task, dan format output yang jelas.
**Why others are wrong:**
- A: Terlalu umum tanpa format.
- C: Terlalu luas dan tidak spesifik.
- D: Tidak menjelaskan hasil.

**Tags:** #prompting #difficulty-easy #type-scenario

---

**Question:** Mengapa set uji kecil penting sebelum rilis?

A) Menggantikan feedback pengguna sepenuhnya.
B) Mengungkap kelemahan output lebih awal.
C) Menghapus kebutuhan prompt spec.
D) Menambah token usage tanpa manfaat.

**Correct:** B

**Why correct:** Uji kecil membantu menemukan masalah sebelum pengguna.
**Why others are wrong:**
- A: Feedback pengguna tetap diperlukan.
- C: Prompt spec tetap penting.
- D: Bukan manfaat utama.

**Tags:** #testing #difficulty-easy #type-definition

---

**Question:** Prompt mencampur dua task sekaligus. Perbaikan terbaik adalah?

A) Tambahkan lebih banyak contoh.
B) Pisahkan menjadi dua prompt atau hilangkan salah satu task.
C) Tambahkan constraints tanpa mengubah struktur.
D) Buat system prompt lebih panjang.

**Correct:** B

**Why correct:** Satu prompt sebaiknya fokus pada satu task.
**Why others are wrong:**
- A: Contoh tidak menyelesaikan task mix.
- C: Constraints tidak cukup.
- D: Menambah panjang tidak menyelesaikan masalah.

**Tags:** #prompting #difficulty-medium #type-scenario

---

**Question:** Input set seperti apa yang terbaik untuk pengujian?

A) Lima input sempurna tanpa variasi.
B) Input realistis dengan variasi dan edge case.
C) Satu input saja karena waktu singkat.
D) Kata acak tanpa konteks dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Variasi dan edge case mengungkap ketidakstabilan.
**Why others are wrong:**
- A: Terlalu ideal dan tidak mewakili pengguna.
- C: Terlalu sedikit untuk uji.
- D: Tidak relevan.

**Tags:** #testing #difficulty-medium #type-scenario

---

**Question:** Output prompt sering melenceng dari format. Perbaikan terbaik?

A) Tambahkan template output yang ketat dan contoh.
B) Hilangkan semua constraints.
C) Hentikan pengujian dalam konteks app AI komersial.
D) Tambahkan randomness dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Template dan contoh mengurangi drift.
**Why others are wrong:**
- B: Membuat output makin tidak konsisten.
- C: Pengujian tetap penting.
- D: Randomness meningkatkan variasi.

**Tags:** #prompting #difficulty-medium #type-scenario

---

**Question:** Prompt spec tidak memiliki role. Risiko utama adalah?

A) Model tidak punya perspektif yang jelas.
B) Respon jadi lebih cepat dalam konteks app AI komersial.
C) Biaya turun otomatis dalam konteks app AI komersial.
D) Akurasi meningkat tanpa sebab.

**Correct:** A

**Why correct:** Role memberi konteks dan perspektif pada output.
**Why others are wrong:**
- B: Kecepatan tidak dijamin.
- C: Biaya tidak otomatis turun.
- D: Akurasi tidak otomatis naik.

**Tags:** #prompting #difficulty-easy #type-definition

---

**Question:** Saat memperpendek prompt, apa yang bisa dihapus dengan aman?

A) Format output dalam konteks app AI komersial.
B) Contoh yang tidak memengaruhi output.
C) Instruksi task utama dalam konteks app AI komersial.
D) Definisi role dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Contoh yang tidak dipakai bisa dihapus tanpa mengurangi kejelasan.
**Why others are wrong:**
- A: Format penting untuk konsistensi.
- C: Task utama wajib ada.
- D: Role memberi konteks.

**Tags:** #prompting #difficulty-medium #type-scenario
