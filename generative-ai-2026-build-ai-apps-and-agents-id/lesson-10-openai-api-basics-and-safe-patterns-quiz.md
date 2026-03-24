# Lesson 10 Quiz Pool

**Question:** Anda membangun app AI dan ingin melindungi API key. Praktik mana yang paling aman untuk lingkungan komersial?

A) Menaruh API key di client dengan obfuscation agar terlihat aman.
B) Menyimpan API key di env variable server dan melakukan request lewat server route.
C) Mengirim API key ke browser agar mudah diganti oleh user.
D) Menaruh API key di local storage untuk cache cepat.

**Correct:** B

**Why correct:** API key harus tetap di server dan tidak boleh di client.
**Why others are wrong:**
- A: Obfuscation tidak melindungi secrets.
- C: Browser bukan tempat aman untuk key.
- D: Local storage juga tidak aman.

**Tags:** #security #difficulty-easy #type-scenario

---

**Question:** OpenAI API mengalami timeout. Pesan apa yang paling baik untuk pengguna agar tetap percaya?

A) “Sistem gagal total, jangan coba lagi.”
B) “Layanan sedang lambat, coba lagi sebentar lagi.”
C) “Kesalahan ini karena Anda.”
D) “Tidak ada respons dan kami hapus input Anda.”

**Correct:** B

**Why correct:** Pesan jelas dengan langkah berikut menjaga kepercayaan.
**Why others are wrong:**
- A: Terlalu keras dan tidak membantu.
- C: Menyalahkan pengguna.
- D: Tidak memberi solusi.

**Tags:** #error-handling #difficulty-medium #type-scenario

---

**Question:** Kombinasi langkah mana yang paling baik untuk menjaga biaya dan stabilitas request?

A) Prompt panjang, logging dimatikan, dan max tokens tanpa batas.
B) Max tokens dibatasi, timeout disetel, dan fallback disiapkan.
C) API key diberikan ke client agar lebih cepat.
D) Validasi input dihapus agar lebih sederhana.

**Correct:** B

**Why correct:** Batas tokens, timeout, dan fallback menjaga stabilitas.
**Why others are wrong:**
- A: Biaya naik dan tidak stabil.
- C: Keys di client tidak aman.
- D: Input tanpa validasi berisiko.

**Tags:** #safety #difficulty-medium #type-scenario

---

**Question:** Anda perlu logging error tanpa melanggar privasi. Cara mana yang paling tepat?

A) Log semua prompt lengkap beserta data pribadi.
B) Gunakan request id, error code, dan ringkasan konteks.
C) Matikan semua logging agar aman.
D) Simpan API key di log agar mudah tracing.

**Correct:** B

**Why correct:** Ringkasan dan request id cukup untuk investigasi.
**Why others are wrong:**
- A: Data pribadi tidak boleh disimpan.
- C: Tanpa log sulit debugging.
- D: Menyimpan API key sangat berbahaya.

**Tags:** #logging #difficulty-medium #type-scenario

---

**Question:** Anda mendapat error 429 rate limit dari OpenAI API. Langkah mana yang paling tepat?

A) Kembalikan fallback, log, dan coba lagi dengan backoff.
B) Kirim stack trace ke pengguna.
C) Kembalikan 500 tanpa pesan.
D) Tambahkan max tokens agar request lebih sedikit.

**Correct:** A

**Why correct:** Fallback, logging, dan retry backoff melindungi UX.
**Why others are wrong:**
- B: Stack trace tidak cocok untuk pengguna.
- C: Tanpa pesan menurunkan kepercayaan.
- D: Max tokens tidak menyelesaikan rate limit.

**Tags:** #rate-limit #difficulty-medium #type-scenario

---

**Question:** Praktik terbaik saat mengelola env variables untuk production adalah apa?

A) Menulis API key di README agar mudah diakses.
B) Gunakan .env lokal dan simpan key di environment production.
C) Simpan API key di client dengan base64.
D) Letakkan API key di test fixtures.

**Correct:** B

**Why correct:** Secrets harus di env dan tidak masuk repo.
**Why others are wrong:**
- A: README bisa bocor.
- C: Base64 bukan keamanan.
- D: Test fixtures bisa bocor.

**Tags:** #deployment #difficulty-easy #type-scenario

---

**Question:** Fallback message yang baik harus seperti apa?

A) “Semua sudah selesai” walau request gagal.
B) “Saat ini belum tersedia, coba lagi sebentar.”
C) “Ini salah pengguna.” dalam konteks app AI komersial.
D) “Kami tutup layanan.” dalam konteks app AI komersial.

**Correct:** B

**Why correct:** Pesan jujur dan memberi langkah berikut.
**Why others are wrong:**
- A: Tidak jujur.
- C: Menyalahkan pengguna.
- D: Tidak membantu.

**Tags:** #fallback #difficulty-easy #type-scenario
