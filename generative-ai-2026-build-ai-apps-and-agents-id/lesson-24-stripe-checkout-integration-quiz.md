# Lesson 24 Quiz Pool

**Question:** Mengapa Stripe checkout cocok untuk solo builder?

A) Karena harus membuat UI pembayaran sendiri.
B) Karena memberi flow aman dan compliance siap pakai.
C) Karena hanya mendukung pembayaran lokal.
D) Karena membuat pembayaran lebih sulit.

**Correct:** B

**Why correct:** Stripe checkout mengurangi beban compliance.
**Why others are wrong:**
- A: UI sudah disediakan.
- C: Stripe mendukung pembayaran global.
- D: Flow justru lebih mudah.

**Tags:** #payments #difficulty-easy #type-definition

---

**Question:** Langkah terbaik sebelum pembayaran nyata adalah?

A) Gunakan test mode dengan kartu uji.
B) Langsung aktifkan ke semua pengguna.
C) Abaikan price id dalam konteks app AI komersial.
D) Kosongkan success URL dalam konteks app AI komersial.

**Correct:** A

**Why correct:** Test mode melindungi dari kesalahan awal.
**Why others are wrong:**
- B: Terlalu berisiko.
- C: Price id harus valid.
- D: Success URL harus diatur.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Risiko jika status pembayaran hanya dari client adalah?

A) Tidak ada risiko dalam konteks app AI komersial.
B) Client bisa memalsukan status.
C) Pembayaran jadi lebih cepat.
D) Validasi jadi tidak perlu.

**Correct:** B

**Why correct:** Client bisa dimanipulasi.
**Why others are wrong:**
- A: Risiko besar.
- C: Keamanan lebih penting.
- D: Validasi tetap perlu.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Success URL berfungsi untuk apa dalam konteks app AI komersial.?

A) Menghapus data dalam konteks app AI komersial.
B) Mengarahkan pengguna kembali setelah pembayaran sukses.
C) Menutup checkout dalam konteks app AI komersial.
D) Menyembunyikan status dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Success URL mengembalikan pengguna ke app.
**Why others are wrong:**
- A: Tidak terkait.
- C: Tidak terkait.
- D: Tidak terkait.

**Tags:** #payments #difficulty-easy #type-definition

---

**Question:** Tanda checkout flow belum benar adalah dalam konteks app AI komersial.?

A) Pengguna melihat status setelah bayar.
B) Pengguna kembali tanpa status.
C) Test mode sukses dalam konteks app AI komersial.
D) Price id valid dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Tanpa status, pengguna bingung.
**Why others are wrong:**
- A: Itu benar.
- C: Itu benar.
- D: Itu benar.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Apa bagian penting saat membuat checkout session?

A) Success URL dan cancel URL.
B) Menaruh API key di client.
C) Menghapus test mode dalam konteks app AI komersial.
D) Menunda validasi dalam konteks app AI komersial.

**Correct:** A

**Why correct:** URL adalah bagian flow pembayaran.
**Why others are wrong:**
- B: Tidak aman.
- C: Test mode penting.
- D: Validasi tetap perlu.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Apa manfaat Stripe test cards dalam konteks app AI komersial.?

A) Untuk pembayaran nyata dalam konteks app AI komersial.
B) Untuk uji tanpa uang nyata.
C) Untuk menyembunyikan error.
D) Untuk menghapus log dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Test cards untuk uji aman.
**Why others are wrong:**
- A: Itu pembayaran nyata.
- C: Bukan fungsinya.
- D: Tidak terkait.

**Tags:** #payments #difficulty-easy #type-definition
