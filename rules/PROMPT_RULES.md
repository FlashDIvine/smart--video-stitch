# Pedoman Mutu & Standard Operating Procedure (SOP) Prompting Video AI
### Framework Rekayasa Prompt Google Veo 3.1 & Flow (High-Consistency & Anti-Artifact Architecture)

Dokumen ini adalah pedoman baku tingkat lanjut untuk menghasilkan video AI berdurasi 8 detik per scene yang stabil, minim halusinasi, sinkron dengan dialog, bebas distorsi anatomi, dan memiliki kontinuitas visual 100% antar-scene.

---

## 1. Mengapa SOP Ini Sangat Krusial?

Model difusi video (seperti Google Veo 3.1) memproses instruksi teks melalui mekanisme *spatio-temporal cross-attention*. Tanpa struktur pemisah yang kaku:
1. **Halusinasi Teks Melayang:** Teks informasi sering kali melayang bebas di udara, terduplikasi di atas kepala karakter, atau berubah menjadi huruf alien.
2. **Distorsi Anatomi & Morfologi (*Morphing*):** Jika terlalu banyak aksi digabung dalam satu kalimat, AI akan "melelehkan" jari tangan (muncul 6–7 jari) atau menyatukan prop ke kulit karakter.
3. **Pusing Kamera (*Wild Camera Wobble*):** Kata kunci seperti *"cinematic dynamic shot"* sering diartikan model sebagai perputaran 360 derajat yang memutarbalikkan ruangan.
4. **Dialog Terpotong:** Kurangnya panduan detik per kata membuat karakter selesai bicara setelah detik ke-8 atau mulai bicara terlambat.

---

## 2. Arsitektur Baku 8-Pilar (The 8-Pillar Prompt Structure)

Setiap scene prompt wajib disusun menggunakan 8 blok hierarki terstruktur berikut:

```text
1. [SHOT AWAL & ENVIRO-PROP ANCHOR]
2. [GERAKAN KAMERA (TIMELINE PER DETIK)]
3. [AKSI KARAKTER & TAMPILAN LAYAR (CHRONOLOGICAL PROGRESSION)]
4. [DETIK DEMI DETIK DETAIL TEKS/GRAFIK]
5. [DIALOG VOKAL & SINKRONISASI GERAK BIBIR]
6. [LARANGAN MUTLAK (ABSOLUTE NEGATIVE CONSTRAINTS)]
7. [GAYA VISUAL, SHADER & AUDIO FOLEY]
8. [FINAL VISUAL PRIORITY HIERARCHY]
```

---

## 3. Rincian & Aturan Setiap Pilar

### Pilar 1: SHOT AWAL & ENVIRO-PROP ANCHOR
* **Framing & Sudut Pandang:** Tetapkan framing awal (misal: *Medium shot*, *Close-up shot*, *Eye level*).
* **Definisi Karakter & Referensi Entitas:** Sebutkan ciri fisik paten (warna rambut, pakaian, prop di tangan).
* **Master Environment Anchor:** Deskripsi latar harus identik antar scene dalam 1 episode agar pencahayaan dan ruangan tidak berubah-ubah.
* **Physical Boundary Lock (Kunci Batas Fisik):**
  > [!IMPORTANT]
  > Teks, angka, grafik, dan UI **HANYA BOLEH MUNCUL DI DALAM BATAS FISIK** monitor komputer, tablet, ponsel, atau panel hologram. **DILARANG KERAS** membiarkan teks melayang bebas di udara!

### Pilar 2: GERAKAN KAMERA TERKUNCi (CAMERA TIMELINE)
Bagi pergerakan kamera ke dalam rentang waktu yang pasti:
* `Detik 0-3`: Kamera statis (*locked-off tripod*).
* `Detik 3-7`: *Slow cinematic push-in* (dolly tipis) ke arah subjek/layar tanpa memotong bingkai.
* `Detik 7-8` (atau 7-10): Kamera kembali secara halus ke medium shot atau tetap stabil.
* ❌ *Dilarang:* *Fast whip pan, 360 rotating tracking, handheld wobble.*

### Pilar 3 & 4: AKSI KARAKTER & TAMPILAN MONITOR SECARA KRONOLOGIS
* Terapkan prinsip **"One Primary Action per Time Window"**:
  - Detik 0–2.5: Aksi A (misal: menunjuk layar, tombol baris 1 muncul).
  - Detik 2.5–5.0: Aksi B (misal: mengetik di keyboard, grafik baris 2 muncul).
  - Detik 5.0–8.0: Aksi C (misal: menoleh ke kamera sambil tersenyum puas).
* Hindari instruksi aksi bertumpuk dalam satu detik.

### Pilar 5: DIALOG VOKAL & SINKRONISASI BIBIR
* **High-Energy Hook Opening:** Untuk scene pembuka (Scene 1), gunakan kalimat vokal yang bertenaga untuk menghentikan jempol penonton (*stop-scrolling hook*):
  - *Contoh:* `"Alamaaaaak! Capenya prompt manual, editing manual, post video manual! Aku bikin tool aja biar AI Agent-ku ngerjain semuanya otomatis!"`
* Tuliskan dialog kata-per-kata diapit tanda petik.
* Sertakan instruksi emosi vokal: *"Ekspresi frustrasi kocak, intonasi vokal lantang dan ekspresif, sinkronisasi gerak bibir natural sesuai bahasa Indonesia."*

### Pilar 6: LARANGAN MUTLAK (STRICT NEGATIVE CONSTRAINTS)
Cantumkan larangan eksplisit untuk mengunci model difusi:
* `Dilarang menampilkan teks melayang di luar batas monitor/papan hologram.`
* `Dilarang morphing atau perubahan bentuk anatomi tubuh.`
* `Tangan wajib memiliki tepat lima jari yang jelas terpisah, tanpa jari ekstra.`
* `Dilarang mengubah properti atau pakaian karakter di tengah scene.`
* `Dilarang menggunakan pergerakan kamera berputar liar.`

### Pilar 7: GAYA VISUAL, SHADER & AUDIO FOLEY
Hindari menyebut merek berhak cipta (misal: "Pixar", "Disney", "iPhone"). Gunakan deskripsi teknis pencahayaan studio 3D:
```text
Clean crisp silhouettes, tactile claymation-inspired smooth matte shaders, soft studio rim lighting, vibrant warm colors, smooth Octane render. Generate with synchronized realistic foley sound effects and clear studio audio.
```

### Pilar 8: FINAL VISUAL PRIORITY (HIERARKI DIFUSI)
Beri panduan prioritas bagi model difusi jika terjadi trade-off rendering:
```text
Character identity and consistency > Content/Logic accuracy > Screen consistency & readability > Scene continuity > Character actions > Camera movement > Decorative effects.
```

---

## 4. Contoh Nyata Template Siap Pakai

### Contoh A: Scene 1 Promo / Hook Dialog (High-Energy Developer Hook)

```text
SHOT AWAL:
Medium shot setinggi mata (eye level), karakter chibi developer dengan kacamata bulat dan hoodie hitam duduk menghadap meja kerja kayu minimalis di ruangan studio modern bergaya 3D semi-realistik. Di atas meja terdapat satu monitor komputer berbingkai tipis yang menampilkan layar terminal kode. Seluruh teks dan UI hanya boleh muncul di dalam batas layar monitor tersebut.

GERAKAN KAMERA:
Detik 0-3: Kamera statis medium shot memperlihatkan karakter sedang memegang kepala dengan ekspresi frustrasi menghadap monitor.
Detik 3-6: Slow push-in tipis ke arah wajah karakter saat berbicara ke kamera.
Detik 6-8: Kamera berhenti stabil, karakter tersenyum penuh percaya diri sambil menunjuk monitor.

AKSI KARAKTER & TAMPILAN MONITOR:
Detik 0-3: Karakter menepuk jidat dengan ekspresi pusing di depan tumpukan tab browser yang terbuka.
Detik 3-6: Karakter menoleh ke arah kamera, berbicara vokal dengan intonasi mengeluh yang ekspresif.
Detik 6-8: Karakter mengetik satu tombol di keyboard mekanikal, layar monitor menampilkan status hijau berkilau: "AUTOMATION ACTIVE 100%". Karakter mengacungkan jempol ke arah kamera.

DIALOG (Bahasa Indonesia):
Developer Chibi: "Alamaaaaak! Capenya prompt manual, editing manual, post video manual! Aku bikin tool aja biar AI Agent-ku ngerjain semuanya otomatis!"

LARANGAN MUTLAK:
- Dilarang menampilkan teks melayang di udara di luar layar monitor.
- Tangan wajib tepat 5 jari yang rapi, tanpa jari ekstra atau menempel ke meja.
- Dilarang morphing wajah atau perubahan warna hoodie.
- Dilarang pergerakan kamera berputar atau berguncang.

GAYA VISUAL:
Stylized 3D animation, Octane render, smooth tactile shaders, warm ambient rim lighting, crisp 4K sharp lines. Suara vokal bahasa Indonesia jernih, suara ketikan keyboard mekanikal renyah (tactile click), dan efek audio "ding" sukses di akhir.

FINAL VISUAL PRIORITY:
Character identity and consistency > Vocal lip sync and emotional expression > Screen text boundary containment > Scene continuity > Lighting and foley sound.
```

---

### Contoh B: Scene Edukasi / Perhitungan Matematika (Chibi & Papan Hologram)

```text
SHOT AWAL:
Medium shot, Nefer chibi (green hair, animal ears, green and gold scholar outfit) berdiri di tengah frame di area terbuka reruntuhan kuno. Di sisi kanan Nefer terdapat SATU papan hologram hijau mint lembut berukuran proporsional untuk menampilkan seluruh perhitungan. Papan hologram merupakan satu-satunya tempat yang boleh menampilkan teks, angka, simbol matematika, dan ilustrasi dadu. Dilarang ada teks melayang di luar batas papan tersebut.

GERAKAN KAMERA:
Detik 0-3: Kamera statis dalam medium shot, informasi kejadian A dan B muncul bertahap di dalam papan.
Detik 3-7: Slow push-in tipis ke arah papan hologram saat baris rumus penjumlahan muncul. Seluruh papan tetap terlihat utuh.
Detik 7-8: Kamera kembali stabil ke medium shot, fokus visual diarahkan ke hasil akhir yang bercahaya lembut.

AKSI KARAKTER & TAMPILAN HOLOGRAM:
Detik 0-2.5: Nefer menunjuk ilustrasi dadu bertitik 2 dengan keterangan "P(A) = 1/6".
Detik 2.5-4.5: Di bawahnya muncul ilustrasi dadu bertitik 5 dengan keterangan "P(B) = 1/6". Nefer menunjuk baris kedua.
Detik 4.5-7.0: Di bawahnya muncul rumus penjumlahan "P(A ∪ B) = 1/6 + 1/6".
Detik 7.0-8.0: Baris hasil akhir muncul "= 2/6 = 1/3" dengan pendar hijau mint lembut. Nefer mengangguk meyakinkan ke arah kamera.

DIALOG (Bahasa Indonesia):
Nefer: "Peluang angka 2 adalah satu per enam, angka 5 juga satu per enam. Jumlahkan, hasilnya dua per enam, atau satu per tiga."

LARANGAN MUTLAK:
- Dilarang menampilkan pecahan secara mendatar dengan garis miring (/); semua pecahan wajib bertingkat vertikal dengan pembilang di atas dan penyebut di bawah.
- Dilarang mengubah nilai hasil akhir selain satu per tiga (1/3).
- Dilarang menampilkan teks di luar bingkai papan hologram.
- Zero morphing pada pakaian dan telinga karakter.

GAYA VISUAL:
Premium anime chibi 3D, garis karakter bersih, palet sejuk ungu-biru dengan pendar hologram hijau mint kontras tinggi. Tipografi matematika tegas dan bercahaya. Suara dialog jernih dan ambient reruntuhan sejuk.

FINAL VISUAL PRIORITY:
Character identity and consistency > Mathematical accuracy > Stacked fraction typography > Hologram text consistency > Character actions > Camera movement.
```

---

## 5. Ringkasan Checklist Sebelum Generate

| No | Parameter Pemeriksaan | Status |
| :--- | :--- | :---: |
| 1 | Apakah ada `SHOT AWAL` dengan batasan layar fisik yang tegas? | [ ] |
| 2 | Apakah durasi pergerakan kamera dipisah per rentang detik (0-3s, 3-7s, dll)? | [ ] |
| 3 | Apakah aksi karakter dibatasi hanya 1 aksi utama per rentang waktu? | [ ] |
| 4 | Apakah ada dialog vokal dengan teks spesifik dan panduan ekspresi/lip-sync? | [ ] |
| 5 | Apakah larangan mutlak (*negative constraints*) tercantum jelas? | [ ] |
| 6 | Apakah hierarki `FINAL VISUAL PRIORITY` dinyatakan di akhir prompt? | [ ] |
| 7 | **Penting:** Apakah seluruh klip dengan dialog vokal digabungkan UTUH tanpa pemotongan ekor? | [ ] |
