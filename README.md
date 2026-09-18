# Monthly Stock & Mutual Fund Screening Agent

Sistem berbasis Python untuk melakukan screening saham dan reksa dana pasar uang secara berkala menggunakan pendekatan rule-based scoring.

Project ini dikembangkan untuk membuat proses screening yang terstruktur, menyimpan hasil historis, mendeteksi perubahan hasil screening, serta menghasilkan laporan secara otomatis.

## Tujuan

- Membuat proses screening yang terstruktur dan dapat dilakukan secara berkala.
- Mengolah data fundamental dan valuasi berdasarkan kriteria yang telah ditentukan.
- Melakukan screening reksa dana pasar uang berdasarkan parameter performa dan risiko.
- Menyimpan hasil screening sebagai data historis.
- Membandingkan hasil screening antar periode.
- Menghasilkan laporan screening secara otomatis.

## Fitur Utama

### 1. Sector-Based Stock Screening

Sistem melakukan screening saham berdasarkan beberapa sektor:

- Banking
- Consumer
- Infrastructure / Telecommunications
- Healthcare

Setiap sektor menggunakan kriteria dan scoring yang disesuaikan dengan karakteristik sektor.

### 2. Fundamental & Valuation Scoring

Parameter yang digunakan meliputi:

- Return on Equity (ROE)
- Pertumbuhan laba
- Pertumbuhan revenue
- Pertumbuhan equity
- Konsistensi laba
- Price-to-Earnings Ratio (PER)
- Price-to-Book Value (PBV)
- Debt-to-Equity Ratio (D/E)
- Free Cash Flow (FCF)

Tidak semua parameter digunakan pada setiap sektor karena metode screening disesuaikan dengan karakteristik masing-masing sektor.

### 3. Money Market Mutual Fund Screening

Screening reksa dana pasar uang menggunakan beberapa parameter:

- Return 1 tahun
- Return 3 tahun
- Usia produk
- Assets Under Management (AUM)
- Risk indicator

### 4. Historical Data Tracking

Hasil screening disimpan dalam format CSV untuk memungkinkan pemantauan perubahan dari waktu ke waktu.

Data yang dicatat meliputi:

- Tanggal dan waktu screening
- Jenis instrumen
- Sektor
- Kode saham
- Nama kandidat
- Score
- Maximum score
- Score percentage
- Status
- Tanggal data
- Sumber data
- Component score

### 5. Screening Comparison

Sistem dapat membandingkan hasil screening terbaru dengan hasil sebelumnya untuk mendeteksi:

- Perubahan kandidat
- Perubahan total score
- Perubahan component score
- Perubahan hasil screening

### 6. Alert System

Sistem memberikan peringatan ketika terdapat:

- Penurunan total score
- Perubahan kandidat
- Penurunan component score

Alert digunakan sebagai informasi untuk pemeriksaan lebih lanjut dan bukan sebagai perintah otomatis untuk membeli atau menjual instrumen investasi.

### 7. Monthly Comparison — V5.6

Sistem melakukan perbandingan berdasarkan snapshot terbaru dari setiap bulan.

Perbandingan dilakukan antara:

- Bulan terbaru
- Bulan sebelumnya

Jika belum tersedia data dari dua bulan berbeda, sistem tidak melakukan perbandingan bulanan.

### 8. Multi-Month Trend Analysis — V5.7

Sistem menyediakan analisis tren multi-bulan untuk melihat perubahan kandidat dan score selama tiga bulan.

Analisis dilakukan setelah tersedia minimal tiga bulan data historis.

### 9. Automated Report Generation

Sistem menghasilkan laporan screening secara otomatis dalam format `.txt`.

Laporan mencakup:

- Hasil screening terbaru
- Perbandingan hasil sebelumnya
- Component score changes
- Alert
- Monthly comparison
- Multi-month trend analysis

### 10. Windows Batch Automation

Seluruh proses dapat dijalankan melalui:

`run_stock_agent.bat`

Dengan demikian, pengguna tidak perlu menjalankan setiap modul Python secara manual.

## Workflow

```text
Data
  ↓
Stock & Mutual Fund Screening
  ↓
Rule-Based Scoring
  ↓
Candidate Selection
  ↓
Historical Data Storage
  ↓
Comparison
  ↓
Alert Detection
  ↓
Monthly Analysis
  ↓
Multi-Month Trend Analysis
  ↓
Automated Report
