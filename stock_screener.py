import yfinance as yf
import math

# ==========================================
# BANK SCREENER V5.3
# SCORING + FILTER LULUS
# ==========================================

daftar_bank = [
    "BBCA.JK",
    "BMRI.JK",
    "BBNI.JK",
    "BRIS.JK",
    "BBTN.JK"
]


# ==========================================
# FUNGSI DASAR
# ==========================================

def angka_valid(nilai):
    try:
        return nilai is not None and not math.isnan(float(nilai))
    except:
        return False


def ambil_nilai(df, nama_baris):
    try:
        if nama_baris not in df.index:
            return None

        data = df.loc[nama_baris].dropna()

        if len(data) == 0:
            return None

        return data

    except:
        return None


def growth(sekarang, sebelumnya):

    if not angka_valid(sekarang):
        return None

    if not angka_valid(sebelumnya):
        return None

    if sebelumnya == 0:
        return None

    return ((sekarang - sebelumnya) / sebelumnya) * 100


def hitung_growth_tahunan(data):

    if data is None or len(data) < 2:
        return None

    return growth(
        data.iloc[0],
        data.iloc[1]
    )


def hitung_konsistensi(data):

    if data is None or len(data) < 2:
        return 0

    jumlah_tumbuh = 0

    for i in range(len(data) - 1):

        sekarang = data.iloc[i]
        sebelumnya = data.iloc[i + 1]

        if angka_valid(sekarang) and angka_valid(sebelumnya):

            if sekarang > sebelumnya:
                jumlah_tumbuh += 1

    return jumlah_tumbuh


# ==========================================
# SCORING
# ==========================================

def score_roe(roe):

    if not angka_valid(roe):
        return 0

    if roe >= 20:
        return 20
    elif roe >= 15:
        return 17
    elif roe >= 12:
        return 14
    elif roe >= 10:
        return 11
    elif roe >= 7:
        return 7
    else:
        return 3


def score_profit_growth(value):

    if not angka_valid(value):
        return 0

    if value >= 15:
        return 15
    elif value >= 10:
        return 13
    elif value >= 5:
        return 11
    elif value > 0:
        return 8
    elif value >= -5:
        return 4
    else:
        return 0


def score_revenue_growth(value):

    if not angka_valid(value):
        return 0

    if value >= 10:
        return 10
    elif value >= 7:
        return 9
    elif value >= 5:
        return 8
    elif value > 0:
        return 6
    elif value >= -5:
        return 3
    else:
        return 0


def score_equity_growth(value):

    if not angka_valid(value):
        return 0

    if value >= 10:
        return 10
    elif value >= 7:
        return 9
    elif value >= 5:
        return 8
    elif value > 0:
        return 6
    elif value >= -5:
        return 3
    else:
        return 0


def score_consistency(jumlah):

    if jumlah >= 3:
        return 15
    elif jumlah == 2:
        return 11
    elif jumlah == 1:
        return 6
    else:
        return 0


def score_per(per):

    if not angka_valid(per) or per <= 0:
        return 0

    if per <= 8:
        return 15
    elif per <= 10:
        return 14
    elif per <= 12:
        return 12
    elif per <= 15:
        return 9
    elif per <= 18:
        return 6
    elif per <= 25:
        return 3
    else:
        return 0


def score_pbv(pbv):

    if not angka_valid(pbv) or pbv <= 0:
        return 0

    if pbv <= 1:
        return 15
    elif pbv <= 1.5:
        return 13
    elif pbv <= 2:
        return 11
    elif pbv <= 3:
        return 8
    elif pbv <= 4:
        return 4
    else:
        return 0


# ==========================================
# SCREENING
# ==========================================

hasil = []


for kode in daftar_bank:

    print("\n" + "=" * 70)
    print(f"MEMERIKSA {kode}")
    print("=" * 70)

    try:

        ticker = yf.Ticker(kode)

        info = ticker.info

        nama = info.get(
            "longName",
            kode
        )

        financials = ticker.financials
        balance = ticker.balance_sheet

        # ==================================
        # LABA
        # ==================================

        laba = ambil_nilai(
            financials,
            "Net Income"
        )

        profit_growth = hitung_growth_tahunan(laba)

        profit_consistency = hitung_konsistensi(laba)

        # ==================================
        # REVENUE
        # ==================================

        revenue = ambil_nilai(
            financials,
            "Total Revenue"
        )

        revenue_growth = hitung_growth_tahunan(revenue)

        # ==================================
        # EKUITAS
        # ==================================

        equity = ambil_nilai(
            balance,
            "Stockholders Equity"
        )

        equity_growth = hitung_growth_tahunan(equity)

        # ==================================
        # PROFITABILITAS
        # ==================================

        roe = info.get("returnOnEquity")

        roe_percent = (
            roe * 100
            if angka_valid(roe)
            else None
        )

        # ==================================
        # VALUASI
        # ==================================

        per = info.get("trailingPE")

        pbv = info.get("priceToBook")

        # ==================================
        # SCORE
        # ==================================

        s_roe = score_roe(
            roe_percent
        )

        s_profit = score_profit_growth(
            profit_growth
        )

        s_revenue = score_revenue_growth(
            revenue_growth
        )

        s_equity = score_equity_growth(
            equity_growth
        )

        s_consistency = score_consistency(
            profit_consistency
        )

        s_per = score_per(
            per
        )

        s_pbv = score_pbv(
            pbv
        )

        total_score = (
            s_roe
            + s_profit
            + s_revenue
            + s_equity
            + s_consistency
            + s_per
            + s_pbv
        )

        # ==================================
        # FILTER MINIMUM
        # ==================================

        syarat_roe = (
            angka_valid(roe_percent)
            and roe_percent >= 10
        )

        syarat_profit = (
            angka_valid(profit_growth)
            and profit_growth > 0
        )

        syarat_revenue = (
            angka_valid(revenue_growth)
            and revenue_growth > 0
        )

        syarat_consistency = (
            profit_consistency >= 2
        )

        # ==================================
        # HITUNG JUMLAH SYARAT
        # ==================================

        jumlah_lulus = sum([
            syarat_roe,
            syarat_profit,
            syarat_revenue,
            syarat_consistency
        ])

        if jumlah_lulus == 4:
            status = "LULUS"
        else:
            status = "TIDAK LULUS"

        # ==================================
        # SIMPAN
        # ==================================

        hasil.append({

            "kode": kode,
            "nama": nama,

            "score": total_score,

            "roe": roe_percent,

            "profit_growth": profit_growth,

            "revenue_growth": revenue_growth,

            "equity_growth": equity_growth,

            "consistency": profit_consistency,

            "per": per,

            "pbv": pbv,

            "syarat_roe": syarat_roe,

            "syarat_profit": syarat_profit,

            "syarat_revenue": syarat_revenue,

            "syarat_consistency": syarat_consistency,

            "status": status,

            "score_roe": s_roe,

            "score_profit": s_profit,

            "score_revenue": s_revenue,

            "score_equity": s_equity,

            "score_consistency": s_consistency,

            "score_per": s_per,

            "score_pbv": s_pbv

        })

        # ==================================
        # HASIL PER BANK
        # ==================================

        print(f"Nama               : {nama}")

        if angka_valid(roe_percent):
            print(
                f"ROE                : "
                f"{roe_percent:.2f}%"
            )
        else:
            print("ROE                : N/A")

        if angka_valid(profit_growth):
            print(
                f"Growth laba        : "
                f"{profit_growth:+.2f}%"
            )
        else:
            print("Growth laba        : N/A")

        if angka_valid(revenue_growth):
            print(
                f"Growth revenue     : "
                f"{revenue_growth:+.2f}%"
            )
        else:
            print("Growth revenue     : N/A")

        if angka_valid(equity_growth):
            print(
                f"Growth equity      : "
                f"{equity_growth:+.2f}%"
            )
        else:
            print("Growth equity      : N/A")

        print(
            f"Konsistensi laba   : "
            f"{profit_consistency}/3"
        )

        if angka_valid(per):
            print(f"PER                : {per:.2f}x")
        else:
            print("PER                : N/A")

        if angka_valid(pbv):
            print(f"PBV                : {pbv:.2f}x")
        else:
            print("PBV                : N/A")

        print("\nFILTER MINIMUM")

        print(
            f"ROE >= 10%         : "
            f"{'PASS' if syarat_roe else 'FAIL'}"
        )

        print(
            f"Growth laba > 0%   : "
            f"{'PASS' if syarat_profit else 'FAIL'}"
        )

        print(
            f"Growth revenue > 0%: "
            f"{'PASS' if syarat_revenue else 'FAIL'}"
        )

        print(
            f"Konsistensi >= 2/3 : "
            f"{'PASS' if syarat_consistency else 'FAIL'}"
        )

        print(
            f"STATUS             : {status}"
        )

        print(
            f"SCORE              : "
            f"{total_score}/100"
        )

    except Exception as e:

        print(f"ERROR: {e}")


# ==========================================
# HASIL FILTER
# ==========================================

lolos = [
    item
    for item in hasil
    if item["status"] == "LULUS"
]


# ==========================================
# RANKING YANG LULUS
# ==========================================

lolos = sorted(
    lolos,
    key=lambda x: x["score"],
    reverse=True
)


print("\n")
print("=" * 70)
print("                 HASIL BANK SCREENING")
print("=" * 70)

if len(lolos) == 0:

    print("Tidak ada bank yang memenuhi")
    print("seluruh syarat minimum.")

else:

    for nomor, item in enumerate(
        lolos,
        start=1
    ):

        print(
            f"{nomor}. "
            f"{item['kode']:<10} "
            f"SCORE: "
            f"{item['score']:>3}/100"
        )


# ==========================================
# KANDIDAT #1
# ==========================================

if len(lolos) > 0:

    kandidat = lolos[0]

    print("\n")
    print("=" * 70)
    print("                 KANDIDAT BANK #1")
    print("=" * 70)

    print(
        f"Kode       : "
        f"{kandidat['kode']}"
    )

    print(
        f"Nama       : "
        f"{kandidat['nama']}"
    )

    print(
        f"Score      : "
        f"{kandidat['score']}/100"
    )

    print(
        f"Status     : "
        f"{kandidat['status']}"
    )

    print("\nDATA UTAMA")
    print("-" * 50)

    if angka_valid(kandidat["roe"]):
        print(
            f"ROE                : "
            f"{kandidat['roe']:.2f}%"
        )

    if angka_valid(kandidat["profit_growth"]):
        print(
            f"Growth laba        : "
            f"{kandidat['profit_growth']:+.2f}%"
        )

    if angka_valid(kandidat["revenue_growth"]):
        print(
            f"Growth revenue     : "
            f"{kandidat['revenue_growth']:+.2f}%"
        )

    if angka_valid(kandidat["equity_growth"]):
        print(
            f"Growth equity      : "
            f"{kandidat['equity_growth']:+.2f}%"
        )

    print(
        f"Konsistensi laba   : "
        f"{kandidat['consistency']}/3"
    )

    if angka_valid(kandidat["per"]):
        print(
            f"PER                : "
            f"{kandidat['per']:.2f}x"
        )

    if angka_valid(kandidat["pbv"]):
        print(
            f"PBV                : "
            f"{kandidat['pbv']:.2f}x"
        )

    print("\nRINCIAN SCORE")
    print("-" * 50)

    print(
        f"ROE                : "
        f"{kandidat['score_roe']}/20"
    )

    print(
        f"Pertumbuhan laba   : "
        f"{kandidat['score_profit']}/15"
    )

    print(
        f"Pertumbuhan revenue: "
        f"{kandidat['score_revenue']}/10"
    )

    print(
        f"Pertumbuhan equity : "
        f"{kandidat['score_equity']}/10"
    )

    print(
        f"Konsistensi laba   : "
        f"{kandidat['score_consistency']}/15"
    )

    print(
        f"PER                : "
        f"{kandidat['score_per']}/15"
    )

    print(
        f"PBV                : "
        f"{kandidat['score_pbv']}/15"
    )


print("\n")
print("=" * 70)
print("BANK SCREENER V5.3 SELESAI")
print("=" * 70)