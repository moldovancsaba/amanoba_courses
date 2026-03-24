# Lesson 22 Quiz Pool

**Question:** Praktik paling aman untuk menyimpan API key di Vercel adalah?

A) Menaruh di code dalam konteks app AI komersial.
B) Menyimpan di env variables.
C) Mengirim ke client dalam konteks app AI komersial.
D) Menaruh di README dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Env variables melindungi secrets.
**Why others are wrong:**
- A: Tidak aman.
- C: Tidak aman.
- D: Tidak aman.

**Tags:** #deployment #difficulty-easy #type-definition

---

**Question:** Tanda env variables belum diatur adalah?

A) Build gagal dan error menyebut key hilang.
B) App berjalan normal dalam konteks app AI komersial.
C) Logs bersih dalam konteks app AI komersial.
D) UI tampil normal dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Error build biasanya menunjukkan env tidak lengkap.
**Why others are wrong:**
- B: Itu tanda env sudah benar.
- C: Itu tanda env sudah benar.
- D: Itu tanda env sudah benar.

**Tags:** #deployment #difficulty-medium #type-scenario

---

**Question:** Mengapa build logs perlu dicek setelah deploy?

A) Untuk menambah latency dalam konteks app AI komersial.
B) Untuk menemukan error lebih cepat.
C) Untuk menyembunyikan masalah.
D) Untuk menambah token dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Logs menunjukkan masalah sebelum pengguna.
**Why others are wrong:**
- A: Tidak relevan.
- C: Kebalikannya.
- D: Tidak relevan.

**Tags:** #deployment #difficulty-easy #type-definition

---

**Question:** Langkah terbaik sebelum mengumumkan URL production adalah?

A) Tidak testing dalam konteks app AI komersial.
B) Menguji endpoint penting.
C) Menaruh API key di client.
D) Menghapus env variables dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Testing memastikan app berjalan.
**Why others are wrong:**
- A: Berisiko.
- C: Tidak aman.
- D: Tidak masuk akal.

**Tags:** #deployment #difficulty-medium #type-scenario

---

**Question:** Mengapa perlu env terpisah untuk staging dan production?

A) Untuk menambah kebingungan.
B) Untuk melindungi data production saat testing.
C) Untuk menambah biaya dalam konteks app AI komersial.
D) Untuk menghapus staging dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Staging menjaga production tetap aman.
**Why others are wrong:**
- A: Bukan tujuan.
- C: Tidak perlu.
- D: Staging tetap berguna.

**Tags:** #deployment #difficulty-medium #type-scenario

---

**Question:** Risiko terbesar menaruh secrets di code adalah?

A) Secrets bisa bocor dan menimbulkan biaya.
B) App jadi lebih cepat dalam konteks app AI komersial.
C) UX meningkat dalam konteks app AI komersial.
D) Lebih mudah maintenance dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Secrets di code mudah diakses publik.
**Why others are wrong:**
- B: Tidak terkait.
- C: Tidak terkait.
- D: Tidak terkait.

**Tags:** #security #difficulty-easy #type-scenario

---

**Question:** Langkah terakhir pada checklist deploy adalah?

A) Mengabaikan logs dalam konteks app AI komersial.
B) Memastikan URL production aktif dan diuji.
C) Menambah randomness dalam konteks app AI komersial.
D) Menaruh secrets di client.

**Correct:** B

**Why correct:** Uji akhir memastikan deploy sukses.
**Why others are wrong:**
- A: Tidak aman.
- C: Tidak relevan.
- D: Tidak aman.

**Tags:** #deployment #difficulty-easy #type-scenario
