import pandas as pd
import os

FILE = "fund_data.csv"

print("=" * 60)
print("MONEY MARKET FUND SCREENER V2")
print("=" * 60)

if not os.path.exists(FILE):
    print("ERROR: fund_data.csv tidak ditemukan.")
    input("\nTekan ENTER untuk keluar...")
    exit()

df = pd.read_csv(FILE)

if df.empty:
    print("\nData reksa dana masih kosong.")
    input("\nTekan ENTER untuk keluar...")
    exit()

print(f"\nJumlah data: {len(df)} reksa dana")

# =========================================================
# KONVERSI DATA ANGKA
# =========================================================

kolom_angka = [
    "Return1Tahun",
    "Return3Tahun",
    "AUM",
    "UsiaTahun",
    "Risiko"
]

for kolom in kolom_angka:
    if kolom in df.columns:
        df[kolom] = pd.to_numeric(df[kolom], errors="coerce")


# =========================================================
# FILTER DASAR
# =========================================================

df = df.dropna(
    subset=["Return1Tahun", "Return3Tahun"]
)

df = df[
    (df["Return1Tahun"] > 0) &
    (df["Return3Tahun"] > 0)
]

if df.empty:
    print("\nTidak ada reksa dana yang memenuhi filter dasar.")
    input("\nTekan ENTER untuk keluar...")
    exit()


# =========================================================
# SCORE RETURN 1 TAHUN - MAX 25
# =========================================================

def score_return_1y(x):
    if x >= 6:
        return 25
    elif x >= 5:
        return 22
    elif x >= 4:
        return 18
    elif x >= 3:
        return 14
    elif x > 0:
        return 8
    return 0


# =========================================================
# SCORE RETURN 3 TAHUN - MAX 25
# =========================================================

def score_return_3y(x):
    if x >= 15:
        return 25
    elif x >= 12:
        return 22
    elif x >= 9:
        return 18
    elif x >= 6:
        return 14
    elif x > 0:
        return 8
    return 0


# =========================================================
# SCORE USIA - MAX 15
# =========================================================

def score_age(x):
    if x >= 5:
        return 15
    elif x >= 3:
        return 12
    elif x >= 1:
        return 8
    return 3


# =========================================================
# SCORE AUM - MAX 15
# =========================================================

def score_aum(x):
    if pd.isna(x):
        return 0
    elif x >= 100_000_000_000:
        return 15
    elif x >= 10_000_000_000:
        return 12
    elif x >= 1_000_000_000:
        return 8
    elif x > 0:
        return 4
    return 0


# =========================================================
# SCORE RISIKO - MAX 20
# Semakin kecil nilai risiko, semakin tinggi skor
# =========================================================

def score_risk(x):
    if pd.isna(x):
        return 0
    elif x <= 0.00010:
        return 20
    elif x <= 0.00015:
        return 17
    elif x <= 0.00020:
        return 14
    elif x <= 0.00030:
        return 10
    elif x <= 0.00050:
        return 6
    else:
        return 2


# =========================================================
# HITUNG SCORE
# =========================================================

df["ScoreReturn1Y"] = df["Return1Tahun"].apply(
    score_return_1y
)

df["ScoreReturn3Y"] = df["Return3Tahun"].apply(
    score_return_3y
)

df["ScoreUsia"] = df["UsiaTahun"].apply(
    score_age
)

df["ScoreAUM"] = df["AUM"].apply(
    score_aum
)

df["ScoreRisiko"] = df["Risiko"].apply(
    score_risk
)

df["Score"] = (
    df["ScoreReturn1Y"] +
    df["ScoreReturn3Y"] +
    df["ScoreUsia"] +
    df["ScoreAUM"] +
    df["ScoreRisiko"]
)

MAX_SCORE = 100

df["ScorePercent"] = (
    df["Score"] / MAX_SCORE * 100
).round(1)

df = df.sort_values(
    by=["Score", "Return1Tahun", "Return3Tahun"],
    ascending=False
)


# =========================================================
# HASIL
# =========================================================

print("\nHASIL SCREENING")
print("-" * 60)

for _, row in df.iterrows():

    print(
        f"{row['Nama']} | "
        f"Score {row['Score']}/{MAX_SCORE} "
        f"({row['ScorePercent']}%)"
    )


# =========================================================
# KANDIDAT UTAMA
# =========================================================

candidate = df.iloc[0]

print("\n" + "=" * 60)
print("KANDIDAT UTAMA")
print("=" * 60)

print(f"Nama            : {candidate['Nama']}")
print(f"Manajer Invest. : {candidate['ManajerInvestasi']}")
print(f"Score           : {candidate['Score']}/{MAX_SCORE}")
print(f"Score %         : {candidate['ScorePercent']}%")
print(f"Return 1 Tahun  : {candidate['Return1Tahun']}%")
print(f"Return 3 Tahun  : {candidate['Return3Tahun']}%")
print(f"AUM             : {candidate['AUM']}")
print(f"Usia            : {candidate['UsiaTahun']} tahun")
print(f"Risiko          : {candidate['Risiko']}")

if "TanggalData" in candidate:
    print(f"Tanggal Data    : {candidate['TanggalData']}")

if "Sumber" in candidate:
    print(f"Sumber          : {candidate['Sumber']}")

print("=" * 60)

input("\nTekan ENTER untuk keluar...")