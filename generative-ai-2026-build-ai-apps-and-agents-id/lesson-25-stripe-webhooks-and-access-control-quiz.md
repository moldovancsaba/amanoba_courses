# Lesson 25 Quiz Pool

**Question:** Mengapa signature verification penting di webhooks?

A) Menambah latency dalam konteks app AI komersial.
B) Memastikan event benar benar dari Stripe.
C) Mengurangi logging dalam konteks app AI komersial.
D) Menambah randomness dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Verifikasi mencegah event palsu.
**Why others are wrong:**
- A: Bukan tujuan.
- C: Logging tetap perlu.
- D: Tidak relevan.

**Tags:** #security #difficulty-easy #type-definition

---

**Question:** Setelah menerima event pembayaran, webhook harus?

A) Update status pembayaran di database.
B) Percaya status dari client.
C) Menutup akses untuk semua.
D) Mengabaikan event dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Status pembayaran menentukan akses.
**Why others are wrong:**
- B: Client bukan sumber kebenaran.
- C: Terlalu ekstrem.
- D: Berisiko kehilangan data.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Risiko jika tidak menggunakan webhooks untuk akses adalah?

A) Tidak ada risiko dalam konteks app AI komersial.
B) Pengguna bisa akses tanpa membayar.
C) App jadi lebih cepat dalam konteks app AI komersial.
D) Logging berkurang dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Status pembayaran bisa salah tanpa webhook.
**Why others are wrong:**
- A: Risiko besar.
- C: Keamanan lebih penting.
- D: Logging bukan tujuan.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Praktik terbaik untuk webhook endpoint adalah?

A) Tidak memverifikasi signature.
B) Memverifikasi signature dan mencatat event.
C) Menaruh API key di client.
D) Menonaktifkan retry dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Verifikasi dan logging menjaga keamanan.
**Why others are wrong:**
- A: Berisiko.
- C: Tidak aman.
- D: Retry penting.

**Tags:** #security #difficulty-medium #type-scenario

---

**Question:** Indikator akses kontrol tidak benar adalah?

A) Pengguna berbayar mendapat akses.
B) Pengguna tidak berbayar mendapat akses.
C) Signature verification berhasil.
D) Log webhook ada dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Akses untuk non bayar adalah masalah.
**Why others are wrong:**
- A: Itu benar.
- C: Itu benar.
- D: Itu benar.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Mengapa retry penting untuk webhooks dalam konteks app AI komersial.?

A) Agar event tidak hilang saat gagal.
B) Agar menambah biaya dalam konteks app AI komersial.
C) Agar membingungkan log dalam konteks app AI komersial.
D) Agar menambah latency dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Retry memastikan event tetap diproses.
**Why others are wrong:**
- B: Bukan tujuan.
- C: Tidak benar.
- D: Tidak relevan.

**Tags:** #reliability #difficulty-medium #type-scenario

---

**Question:** Setelah status pembayaran diperbarui, langkah berikutnya adalah?

A) Kontrol akses berdasarkan status.
B) Menonaktifkan database dalam konteks app AI komersial.
C) Menulis status di client saja.
D) Menghapus logging dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Akses harus mengikuti status pembayaran.
**Why others are wrong:**
- B: Tidak masuk akal.
- C: Client bukan sumber kebenaran.
- D: Logging tetap perlu.

**Tags:** #payments #difficulty-easy #type-scenario
