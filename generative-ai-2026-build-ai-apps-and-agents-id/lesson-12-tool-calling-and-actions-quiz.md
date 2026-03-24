# Lesson 12 Quiz Pool

**Question:** Tool schema yang baik harus mencakup apa saja?

A) Nama tool saja dalam konteks app AI komersial.
B) Nama tool, input fields, dan output shape.
C) Output saja tanpa input dalam konteks app AI komersial.
D) Deskripsi pemasaran dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Input dan output harus jelas agar call stabil.
**Why others are wrong:**
- A: Tidak cukup untuk validasi.
- C: Input tetap dibutuhkan.
- D: Pemasaran bukan schema.

**Tags:** #tools #difficulty-easy #type-definition

---

**Question:** Tool bisa mengubah data pengguna. Guardrail terbaik adalah?

A) Jalankan tanpa validasi agar cepat.
B) Tambahkan konfirmasi pengguna sebelum eksekusi.
C) Sembunyikan action di UI tetapi tetap jalankan.
D) Matikan logging untuk menghindari data.

**Correct:** B

**Why correct:** Konfirmasi mengurangi risiko tindakan tidak diinginkan.
**Why others are wrong:**
- A: Tanpa validasi berbahaya.
- C: Tetap berisiko.
- D: Logging penting untuk audit.

**Tags:** #guardrails #difficulty-medium #type-scenario

---

**Question:** Tool call sering gagal karena input buruk. Tindakan terbaik?

A) Biarkan model menebak input.
B) Validasi input sebelum memanggil tool.
C) Tambah randomness agar input berubah.
D) Hapus schema dan gunakan teks bebas.

**Correct:** B

**Why correct:** Validasi input mencegah error.
**Why others are wrong:**
- A: Tebakan meningkatkan error.
- C: Randomness tidak memperbaiki kualitas.
- D: Teks bebas lebih berisiko.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** Apa arti guardrail dalam tool calling dalam konteks app AI komersial.?

A) Aturan yang mencegah action berbahaya.
B) Cara menambah token usage.
C) Penyimpanan output dalam konteks app AI komersial.
D) Pengganti logging dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Guardrail melindungi dari tindakan yang tidak diinginkan.
**Why others are wrong:**
- B: Tidak terkait.
- C: Bukan fungsi guardrail.
- D: Logging tetap dibutuhkan.

**Tags:** #guardrails #difficulty-easy #type-definition

---

**Question:** Indikator tool calling yang buruk adalah?

A) Call sering gagal karena input salah.
B) Log mencatat semua action.
C) Schema memiliki required fields.
D) Ada konfirmasi untuk action berisiko.

**Correct:** A

**Why correct:** Kegagalan input menandakan schema atau validasi lemah.
**Why others are wrong:**
- B: Itu praktik baik.
- C: Itu praktik baik.
- D: Itu praktik baik.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** Strategi aman untuk tool baru di rilis awal adalah?

A) Membuka semua tools sekaligus.
B) Mulai dari satu tool dengan schema jelas dan guardrails dasar.
C) Menghapus logging dalam konteks app AI komersial.
D) Tidak menulis schema sama sekali.

**Correct:** B

**Why correct:** Fokus pada satu tool mengurangi risiko.
**Why others are wrong:**
- A: Risiko meningkat.
- C: Logging penting.
- D: Schema wajib.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** Mengapa action log penting untuk tool calls?

A) Agar bisa menelusuri kejadian dan memperbaiki error.
B) Agar menambah latency dalam konteks app AI komersial.
C) Agar menyembunyikan masalah.
D) Agar tidak ada data sama sekali.

**Correct:** A

**Why correct:** Log membantu audit dan debugging.
**Why others are wrong:**
- B: Latency bukan tujuan.
- C: Menyembunyikan masalah berbahaya.
- D: Data tetap diperlukan.

**Tags:** #logging #difficulty-easy #type-definition
