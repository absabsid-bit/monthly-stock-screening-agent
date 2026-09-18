import subprocess
import sys
import re
import csv
import os
import subprocess
from datetime import datetime

# ============================================================
# MASTER STOCK AGENT V5
# 1 Reksa Dana + 4 Saham
# + Perbandingan dengan screening sebelumnya
# ============================================================

SCREENER = [
    ("BANK", "stock_screener.py"),
    ("CONSUMER", "consumer_screener_v2.py"),
    ("INFRASTRUCTURE / TELECOM", "infrastructure_screener.py"),
    ("HEALTHCARE", "healthcare_screener.py"),
]

FUND_SCREENER = "money_market_screener_v2.py"

COMPANY_NAMES = {
    "BRIS.JK": "PT Bank Syariah Indonesia Tbk",
    "INDF.JK": "PT Indofood Sukses Makmur Tbk",
    "ISAT.JK": "PT Indosat Tbk",
    "MIKA.JK": "PT Mitra Keluarga Karyasehat Tbk",
}

HISTORY_FILE = "screening_history.csv"


# ============================================================
# JALANKAN PROGRAM
# ============================================================

def run_program(label, filename):

    print("\n" + "=" * 70)
    print(f" MENJALANKAN {label}")
    print("=" * 70)

    if not os.path.exists(filename):
        print(f"ERROR: File {filename} tidak ditemukan.")
        return ""

    try:

        result = subprocess.run(
    [sys.executable, filename],
    capture_output=True,
    text=True,
    input="\n"
)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        return result.stdout

    except Exception as e:

        print(f"ERROR menjalankan {filename}: {e}")
        return ""


# ============================================================
# AMBIL KANDIDAT SAHAM
# ============================================================

def extract_stock_candidate(output):

    code_match = re.search(
        r"Kode\s*:\s*([A-Z0-9.-]+)",
        output
    )

    score_match = re.search(
        r"Score\s*:\s*([0-9]+)\s*/\s*([0-9]+)",
        output
    )

    status_match = re.search(
        r"Status\s*:\s*(.+)",
        output
    )

    if not code_match:
        return None

    code = code_match.group(1).strip()

    if score_match:
        score = int(score_match.group(1))
        maximum = int(score_match.group(2))
    else:
        score = 0
        maximum = 0

    if status_match:
        status = status_match.group(1).strip()
    else:
        status = "-"

    name = COMPANY_NAMES.get(
        code,
        "Nama tidak tersedia"
    )

    # ==========================================
    # COMPONENT SCORE
    # ==========================================

    score_roe_match = re.search(
        r"ROE\s*:\s*([0-9]+)\s*/\s*20",
        output
    )

    score_profit_match = re.search(
        r"Pertumbuhan laba\s*:\s*([0-9]+)\s*/\s*15",
        output
    )

    score_revenue_match = re.search(
        r"Pertumbuhan revenue\s*:\s*([0-9]+)\s*/\s*10",
        output
    )

    score_equity_match = re.search(
        r"Pertumbuhan equity\s*:\s*([0-9]+)\s*/\s*10",
        output
    )

    score_consistency_match = re.search(
        r"Konsistensi laba\s*:\s*([0-9]+)\s*/\s*15",
        output
    )

    score_per_match = re.search(
        r"PER\s*:\s*([0-9]+)\s*/\s*15",
        output
    )

    score_pbv_match = re.search(
        r"PBV\s*:\s*([0-9]+)\s*/\s*15",
        output
    )

    score_roe = (
        int(score_roe_match.group(1))
        if score_roe_match else 0
    )

    score_profit = (
        int(score_profit_match.group(1))
        if score_profit_match else 0
    )

    score_revenue = (
        int(score_revenue_match.group(1))
        if score_revenue_match else 0
    )

    score_equity = (
        int(score_equity_match.group(1))
        if score_equity_match else 0
    )

    score_consistency = (
        int(score_consistency_match.group(1))
        if score_consistency_match else 0
    )

    score_per = (
        int(score_per_match.group(1))
        if score_per_match else 0
    )

    score_pbv = (
        int(score_pbv_match.group(1))
        if score_pbv_match else 0
    )

    # ==========================================
    # SCORE PERCENT
    # ==========================================

    if maximum > 0:
        score_percent = (score / maximum) * 100
    else:
        score_percent = 0

    # ==========================================
    # RETURN
    # ==========================================

    return {
        "type": "SAHAM",
        "code": code,
        "name": name,
        "score": score,
        "maximum": maximum,
        "score_percent": score_percent,
        "status": status,
        "score_roe": score_roe,
        "score_profit": score_profit,
        "score_revenue": score_revenue,
        "score_equity": score_equity,
        "score_consistency": score_consistency,
        "score_per": score_per,
        "score_pbv": score_pbv,
    }

# ============================================================
# AMBIL KANDIDAT REKSA DANA
# ============================================================

def extract_fund_candidate(output):

    name_match = re.search(
        r"Nama\s+:\s*(.+)",
        output
    )

    manager_match = re.search(
        r"Manajer Invest\.\s*:\s*(.+)",
        output
    )

    score_match = re.search(
        r"Score\s+:\s*([0-9]+)\s*/\s*([0-9]+)",
        output
    )

    data_date_match = re.search(
        r"Tanggal Data\s*:\s*(\d{4}-\d{2}-\d{2})",
        output
    )

    source_match = re.search(
        r"Sumber\s*:\s*(.+)",
        output
    )

    if not name_match:
        return None

    name = name_match.group(1).strip()

    if manager_match:
        manager = manager_match.group(1).strip()
    else:
        manager = "-"

    if score_match:
        score = int(score_match.group(1))
        maximum = int(score_match.group(2))
    else:
        score = 0
        maximum = 0

    if maximum > 0:
        score_percent = (score / maximum) * 100
    else:
        score_percent = 0

    if data_date_match:
        data_date = data_date_match.group(1).strip()
    else:
        data_date = "-"

    if source_match:
        source = source_match.group(1).strip()
    else:
        source = "-"

    return {
        "type": "REKSA DANA",
        "code": "-",
        "name": name,
        "manager": manager,
        "score": score,
        "maximum": maximum,
        "score_percent": score_percent,
        "status": "LULUS",
        "data_date": data_date,
        "source": source,
    }


# ============================================================
# BACA HISTORY LAMA
# Mendukung format V3 dan V4
# ============================================================

def load_previous_history():

    previous = {}

    if not os.path.exists(HISTORY_FILE):
        return previous

    try:

        with open(
            HISTORY_FILE,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.reader(file)

            rows = list(reader)

        if len(rows) <= 1:
            return previous

        header = rows[0]

        # Cari posisi kolom berdasarkan nama header jika tersedia
        header_map = {
            name.strip(): i
            for i, name in enumerate(header)
        }

        for row in rows[1:]:

            if len(row) == 0:
                continue

            try:

                # Format V4/V4.1
                if "Jenis" in header_map:

                    jenis = row[header_map["Jenis"]].strip()

                else:

                    # Format V3 lama
                    jenis = "SAHAM"

                sektor = row[
                    header_map["Sektor"]
                ].strip()

                kode = row[
                    header_map["Kode"]
                ].strip()

                nama = row[
                    header_map["Nama"]
                ].strip()

                score = float(
                    row[header_map["Score"]]
                )

                maximum = float(
                    row[header_map["MaximumScore"]]
                )

                tanggal = row[
                    header_map["Tanggal"]
                ].strip()

                waktu = row[
                    header_map["Waktu"]
                ].strip()

                key = sektor

                previous[key] = {
    "type": jenis,
    "sector": sektor,
    "code": kode,
    "name": nama,
    "score": score,
    "maximum": maximum,
    "tanggal": tanggal,
    "waktu": waktu,

    # COMPONENT SCORE
    "score_roe": row[header_map["Score_ROE"]].strip()
        if "Score_ROE" in header_map else "-",

    "score_profit": row[header_map["Score_Profit"]].strip()
        if "Score_Profit" in header_map else "-",

    "score_revenue": row[header_map["Score_Revenue"]].strip()
        if "Score_Revenue" in header_map else "-",

    "score_equity": row[header_map["Score_Equity"]].strip()
        if "Score_Equity" in header_map else "-",

    "score_consistency": row[header_map["Score_Consistency"]].strip()
        if "Score_Consistency" in header_map else "-",

    "score_per": row[header_map["Score_PER"]].strip()
        if "Score_PER" in header_map else "-",

    "score_pbv": row[header_map["Score_PBV"]].strip()
        if "Score_PBV" in header_map else "-",
}

            except (KeyError, IndexError, ValueError):
                # Abaikan baris history yang rusak/tidak lengkap
                continue

    except Exception as e:

        print(
            f"PERINGATAN: History tidak dapat dibaca: {e}"
        )

    return previous


# ============================================================
# TAMPILKAN PERBANDINGAN + DETEKSI PERUBAHAN
# ============================================================

def show_comparison(candidates, previous):

    print("\n")
    print("=" * 70)
    print("PERUBAHAN SCREENING")
    print("=" * 70)

    if not previous:

        print(
            "Belum ada data screening sebelumnya "
            "yang dapat dibandingkan."
        )

        return

    for candidate in candidates:

        sector = candidate["sector"]

        old = previous.get(sector)

        print("\n" + sector)
        print("-" * 70)

        print(
            f"Sekarang   : {candidate['name']}"
        )

        print(
            f"Score      : "
            f"{candidate['score']}/{candidate['maximum']}"
        )

        if not old:

            print(
                "Sebelumnya : Belum ada data"
            )

            print(
                "STATUS     : DATA PERTAMA"
            )

            continue

        print(
            f"Sebelumnya : {old['name']}"
        )

        print(
            f"Score lama : "
            f"{int(old['score'])}/{int(old['maximum'])}"
        )

        score_change = (
            candidate["score"] -
            old["score"]
        )

        if score_change > 0:
            change_text = f"+{score_change:g}"
            score_status = "SCORE NAIK"
        elif score_change < 0:
            change_text = f"{score_change:g}"
            score_status = "SCORE TURUN"
        else:
            change_text = "0"
            score_status = "SCORE TETAP"

        print(
            f"Perubahan  : {change_text}"
        )

        print(
            f"Status skor: {score_status}"
        )

        # Identitas kandidat
        current_identifier = (
            candidate["code"]
            if candidate["type"] == "SAHAM"
            else candidate["name"]
        )

        old_identifier = (
            old["code"]
            if old["type"] == "SAHAM"
            else old["name"]
        )

        if current_identifier != old_identifier:

            print(
                "Kandidat   : BERUBAH"
            )

            print(
                f"   Lama     : {old['name']}"
            )

            print(
                f"   Sekarang : {candidate['name']}"
            )

        else:

            print(
                "Kandidat   : TETAP"
            )

        print(
            f"Data lama  : "
            f"{old['tanggal']} {old['waktu']}"
        )

        # Peringatan jika skor turun
        if score_change < 0:

            print(
                "PERINGATAN : Skor kandidat mengalami penurunan."
            )

        # Peringatan jika kandidat berubah
        if current_identifier != old_identifier:

            print(
                "PERINGATAN : Kandidat sektor berubah."
            )


# ============================================================
# CEK KESEGARAN DATA REKSA DANA
# ============================================================

def show_data_freshness(candidates):

    print("\n")
    print("=" * 70)
    print("CEK KESEGARAN DATA")
    print("=" * 70)

    today = datetime.now().date()

    for candidate in candidates:

        if candidate["type"] == "REKSA DANA":

            data_date = candidate.get(
                "data_date",
                "-"
            )

            print("\nREKSA DANA PASAR UANG")
            print("-" * 70)
            print(f"Tanggal data : {data_date}")
            print(f"Sumber       : {candidate.get('source', '-')}")

            if data_date != "-":

                try:

                    parsed_date = datetime.strptime(
                        data_date,
                        "%Y-%m-%d"
                    ).date()

                    age_days = (
                        today - parsed_date
                    ).days

                    print(
                        f"Umur data    : {age_days} hari"
                    )

                    if age_days <= 45:
                        print(
                            "Status data  : MASIH RELATIF TERBARU"
                        )
                    elif age_days <= 90:
                        print(
                            "Status data  : PERLU DIPERBARUI"
                        )
                    else:
                        print(
                            "Status data  : DATA SUDAH LAMA"
                        )

                except ValueError:

                    print(
                        "Status data  : FORMAT TANGGAL TIDAK VALID"
                    )

        else:

            print(
                f"{candidate['sector']:<28} "
                f"Data: hasil screening saat program dijalankan "
                f"(sumber screener: yfinance)"
            )


# ============================================================
# SIMPAN HISTORY
# ============================================================

def save_history(candidates):

    fieldnames = [
        "Tanggal",
        "Waktu",
        "Jenis",
        "Sektor",
        "Kode",
        "Nama",
        "ManajerInvestasi",
        "Score",
        "MaximumScore",
        "ScorePercent",
       "Status",
"TanggalData",
"Sumber",
"Score_ROE",
"Score_Profit",
"Score_Revenue",
"Score_Equity",
"Score_Consistency",
"Score_PER",
"Score_PBV"
    ]

    file_exists = os.path.exists(HISTORY_FILE)

    now = datetime.now()

    run_date = now.strftime("%Y-%m-%d")
    run_time = now.strftime("%H:%M:%S")

    with open(
        HISTORY_FILE,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists:
            writer.writeheader()

        for candidate in candidates:

            writer.writerow({
                "Tanggal": run_date,
                "Waktu": run_time,
                "Jenis": candidate["type"],
                "Sektor": candidate["sector"],
                "Kode": candidate["code"],
                "Nama": candidate["name"],
                "ManajerInvestasi": candidate.get(
                    "manager",
                    "-"
                ),
                "Score": candidate["score"],
                "MaximumScore": candidate["maximum"],
                "ScorePercent": round(
                    candidate["score_percent"],
                    2
                ),
                "Status": candidate["status"],
                "TanggalData": candidate.get(
                    "data_date",
                    run_date
                ),
                "Sumber": candidate.get(
                    "source",
                    "yfinance"
                    if candidate["type"] == "SAHAM"
                    else "-"
                ),

                "Score_ROE": candidate.get(
                    "score_roe",
                    "-"
                ),

                "Score_Profit": candidate.get(
                    "score_profit",
                    "-"
                ),

                "Score_Revenue": candidate.get(
                    "score_revenue",
                    "-"
                ),

                "Score_Equity": candidate.get(
                    "score_equity",
                    "-"
                ),

                "Score_Consistency": candidate.get(
                    "score_consistency",
                    "-"
                ),

                "Score_PER": candidate.get(
                    "score_per",
                    "-"
                ),

                "Score_PBV": candidate.get(
                    "score_pbv",
                    "-"
                )
            })


# ============================================================
# MULAI MASTER AGENT
# ============================================================

# Baca history SEBELUM menyimpan hasil screening baru
previous_history = load_previous_history()

candidates = []


# ============================================================
# REKSA DANA
# ============================================================

fund_output = run_program(
    "REKSA DANA",
    FUND_SCREENER
)

fund_candidate = extract_fund_candidate(
    fund_output
)

if fund_candidate:

    candidates.append({
        "sector": "REKSA DANA PASAR UANG",
        **fund_candidate
    })


# ============================================================
# SAHAM
# ============================================================

for sector, filename in SCREENER:

    output = run_program(
        sector,
        filename
    )

    candidate = extract_stock_candidate(
        output
    )

    if candidate:

        candidates.append({
            "sector": sector,
            **candidate
        })


# ============================================================
# LAPORAN MASTER
# ============================================================

print("\n")
print("=" * 70)
print("              MASTER STOCK AGENT V5")
print("=" * 70)

print("\nHASIL SCREENING")
print("-" * 70)

for i, candidate in enumerate(
    candidates,
    start=1
):

    print(
        f"{i}. {candidate['sector']}"
    )

    if candidate["type"] == "REKSA DANA":

        print(
            "   Jenis      : REKSA DANA PASAR UANG"
        )

        print(
            f"   Nama       : "
            f"{candidate['name']}"
        )

        print(
            f"   Manajer    : "
            f"{candidate['manager']}"
        )

    else:

        print(
            f"   Kode       : "
            f"{candidate['code']}"
        )

        print(
            f"   Nama       : "
            f"{candidate['name']}"
        )

    print(
        f"   Score      : "
        f"{candidate['score']}/"
        f"{candidate['maximum']}"
    )

    print(
        f"   Score %    : "
        f"{candidate['score_percent']:.1f}%"
    )

    print(
        f"   Status     : "
        f"{candidate['status']}"
    )

    print()
# ============================================================
# PERBANDINGAN COMPONENT SCORE
# ============================================================

def show_component_changes(candidates, previous):

    print("\n")
    print("=" * 70)
    print("PERUBAHAN COMPONENT SCORE")
    print("=" * 70)

    found_change = False

    component_names = {
        "score_roe": "ROE",
        "score_profit": "Pertumbuhan laba",
        "score_revenue": "Pertumbuhan revenue",
        "score_equity": "Pertumbuhan equity",
        "score_consistency": "Konsistensi laba",
        "score_per": "PER",
        "score_pbv": "PBV"
    }

    for candidate in candidates:

        if candidate["type"] != "SAHAM":
            continue

        sector = candidate["sector"]
        old = previous.get(sector)

        if not old:
            continue

        if "score_roe" not in old:
            continue

        component_changes = []

        for key, label in component_names.items():

            current_value = candidate.get(key)
            old_value = old.get(key)

            if current_value is None or old_value is None:
                continue

            try:
                current_value = int(current_value)
                old_value = int(old_value)
            except (ValueError, TypeError):
                continue

            if current_value != old_value:

                component_changes.append(
                    (
                        label,
                        old_value,
                        current_value,
                        current_value - old_value
                    )
                )

        if component_changes:

            found_change = True

            print("\n" + sector)
            print("-" * 70)
            print(f"Kandidat : {candidate['name']}")
            print(
                f"Total Score : "
                f"{old['score']} → {candidate['score']}"
            )

            print("PERUBAHAN KOMPONEN")

            for label, old_value, current_value, change in component_changes:

                if change > 0:
                    change_text = f"+{change}"
                else:
                    change_text = f"{change}"

                print(
                    f"{label:<22}: "
                    f"{old_value} → {current_value} "
                    f"({change_text})"
                )

    print("\n" + "-" * 70)

    if not found_change:
        print(
            "Tidak ada perubahan component score "
            "pada kandidat saham."
        )

# ============================================================
# RINGKASAN PERUBAHAN
# ============================================================

def show_change_summary(candidates, previous):

    print("\n")
    print("=" * 70)
    print("RINGKASAN PERUBAHAN")
    print("=" * 70)

    if not previous:
        print("Belum ada history sebelumnya.")
        print("Belum dapat membandingkan perubahan.")
        return

    changes_found = False
    score_down = False
    candidate_changed = False

    for candidate in candidates:

        sector = candidate["sector"]
        old = previous.get(sector)

        if not old:
            print(f"{sector:<28}: DATA PERTAMA")
            continue

        score_change = (
            candidate["score"] - old["score"]
        )

        current_identifier = (
            candidate["code"]
            if candidate["type"] == "SAHAM"
            else candidate["name"]
        )

        old_identifier = (
            old["code"]
            if old["type"] == "SAHAM"
            else old["name"]
        )

        candidate_change = (
            current_identifier != old_identifier
        )

        if score_change > 0:

            print(
                f"{sector:<28}: SCORE NAIK +{score_change:g}"
            )

            changes_found = True

        elif score_change < 0:

            print(
                f"{sector:<28}: SCORE TURUN {score_change:g}"
            )

            changes_found = True
            score_down = True

        else:

            print(
                f"{sector:<28}: SCORE TETAP"
            )

        if candidate_change:

            print(
                f"   Kandidat berubah: "
                f"{old['name']} -> {candidate['name']}"
            )

            changes_found = True
            candidate_changed = True

    print("-" * 70)

    if not changes_found:

        print(
            "Tidak ada perubahan sejak screening sebelumnya."
        )

    if score_down:

        print(
            "PERHATIAN: Ada score yang mengalami penurunan."
        )

    if candidate_changed:

        print(
            "PERHATIAN: Ada kandidat sektor yang berubah."
        )

    if not score_down and not candidate_changed:

        print(
            "Tidak ada penurunan score atau perubahan kandidat."
        )
# ============================================================
# CEK KESEGARAN DATA
# ============================================================

show_data_freshness(
    candidates
)

# ============================================================
# RINGKASAN PERINGATAN V5.3
# ============================================================

def show_alert_summary(candidates, previous):

    print("\n")
    print("=" * 70)
    print("RINGKASAN PERINGATAN")
    print("=" * 70)

    alerts_found = False

    component_names = {
        "score_roe": "ROE",
        "score_profit": "Pertumbuhan laba",
        "score_revenue": "Pertumbuhan revenue",
        "score_equity": "Pertumbuhan equity",
        "score_consistency": "Konsistensi laba",
        "score_per": "PER",
        "score_pbv": "PBV"
    }

    for candidate in candidates:

        sector = candidate["sector"]
        old = previous.get(sector)

        if not old:
            continue

        score_change = (
            candidate["score"] - old["score"]
        )

        current_identifier = (
            candidate["code"]
            if candidate["type"] == "SAHAM"
            else candidate["name"]
        )

        old_identifier = (
            old["code"]
            if old["type"] == "SAHAM"
            else old["name"]
        )

        candidate_changed = (
            current_identifier != old_identifier
        )

        # ----------------------------------------------------
        # PERINGATAN SCORE TURUN
        # ----------------------------------------------------

        if score_change < 0:

            alerts_found = True

            print("\nPERINGATAN SCORE TURUN")
            print("-" * 70)
            print(f"Sektor           : {sector}")
            print(f"Kandidat         : {candidate['name']}")
            print(
                f"Score sebelumnya : "
                f"{int(old['score'])}/{int(old['maximum'])}"
            )
            print(
                f"Score sekarang   : "
                f"{candidate['score']}/{candidate['maximum']}"
            )
            print(
                f"Perubahan        : "
                f"{score_change:g}"
            )
            print(
                "Tindakan         : "
                "Periksa kembali data fundamental."
            )

        # ----------------------------------------------------
        # PERINGATAN KANDIDAT BERUBAH
        # ----------------------------------------------------

        if candidate_changed:

            alerts_found = True

            print("\nKANDIDAT BERUBAH")
            print("-" * 70)
            print(f"Sektor           : {sector}")
            print(f"Sebelumnya       : {old['name']}")
            print(f"Sekarang         : {candidate['name']}")
            print(
                "Tindakan         : "
                "Periksa kembali kedua kandidat."
            )

        # ----------------------------------------------------
        # PERINGATAN COMPONENT SCORE TURUN
        # ----------------------------------------------------

        if candidate["type"] != "SAHAM":
            continue

        component_alerts = []

        for key, label in component_names.items():

            current_value = candidate.get(key)
            old_value = old.get(key)

            if current_value is None or old_value is None:
                continue

            try:
                current_value = int(current_value)
                old_value = int(old_value)
            except (ValueError, TypeError):
                continue

            change = current_value - old_value

            if change < 0:

                component_alerts.append(
                    (
                        label,
                        old_value,
                        current_value,
                        change
                    )
                )

        # ----------------------------------------------------
        # TAMPILKAN COMPONENT ALERT
        # ----------------------------------------------------

        if component_alerts:

            alerts_found = True

            print("\nPERINGATAN COMPONENT SCORE TURUN")
            print("-" * 70)
            print(f"Sektor   : {sector}")
            print(f"Kandidat : {candidate['name']}")

            for (
                label,
                old_value,
                current_value,
                change
            ) in component_alerts:

                print(
                    f"{label:<22}: "
                    f"{old_value} → {current_value} "
                    f"({change})"
                )

            print(
                "Tindakan : "
                "Periksa penyebab perubahan komponen."
            )

    print("\n" + "-" * 70)

    if not alerts_found:

        print(
            "OK: Tidak ada penurunan score, "
            "penurunan component score, "
            "atau perubahan kandidat."
        )

    else:

        print(
            "Ada perubahan yang perlu diperiksa "
            "sebelum mengambil keputusan investasi."
        )

# ============================================================
# PERBANDINGAN HISTORY
# ============================================================

show_comparison(
    candidates,
    previous_history
)
show_change_summary(
    candidates,
    previous_history
)
show_component_changes(
    candidates,
    previous_history
)
show_alert_summary(
    candidates,
    previous_history
)


# ============================================================
# V5.6 - PERBANDINGAN BULANAN
# ============================================================

def get_monthly_snapshots():

    import csv
    from collections import defaultdict

    history_file = "screening_history.csv"

    monthly_data = defaultdict(list)

    try:
        with open(
            history_file,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                tanggal = row.get("Tanggal", "").strip()
                waktu = row.get("Waktu", "").strip()

                if not tanggal or not waktu:
                    continue

                bulan = tanggal[:7]

                monthly_data[bulan].append(row)

    except FileNotFoundError:

        print(
            "PERINGATAN: screening_history.csv tidak ditemukan."
        )

        return {}

    monthly_snapshots = {}

    for bulan, rows in monthly_data.items():

        timestamps = []

        for row in rows:

            tanggal = row.get("Tanggal", "").strip()
            waktu = row.get("Waktu", "").strip()

            if tanggal and waktu:

                timestamps.append(
                    f"{tanggal} {waktu}"
                )

        if not timestamps:
            continue

        latest_timestamp = max(timestamps)

        snapshot_rows = []

        for row in rows:

            timestamp = (
                row.get("Tanggal", "").strip()
                + " "
                + row.get("Waktu", "").strip()
            )

            if timestamp == latest_timestamp:

                snapshot_rows.append(row)

        monthly_snapshots[bulan] = {
            "timestamp": latest_timestamp,
            "rows": snapshot_rows
        }

    return monthly_snapshots


def show_monthly_comparison():

    print("\n")
    print("=" * 70)
    print("PERBANDINGAN BULANAN V5.6")
    print("=" * 70)

    monthly_snapshots = get_monthly_snapshots()

    if not monthly_snapshots:

        print(
            "Belum ada data screening bulanan."
        )

        return

    months = sorted(
        monthly_snapshots.keys(),
        reverse=True
    )

    current_month = months[0]

    print(
        f"\nBulan terbaru : {current_month}"
    )

    if len(months) < 2:

        print(
            "Belum ada bulan sebelumnya "
            "untuk dibandingkan."
        )

        print(
            "Minimal diperlukan data "
            "dari 2 bulan berbeda."
        )

        return

    previous_month = months[1]

    current_snapshot = (
        monthly_snapshots[current_month]
    )

    previous_snapshot = (
        monthly_snapshots[previous_month]
    )

    print(
        f"Bulan sebelumnya : {previous_month}"
    )

    print(
        f"\nSnapshot terbaru    : "
        f"{current_snapshot['timestamp']}"
    )

    print(
        f"Snapshot sebelumnya : "
        f"{previous_snapshot['timestamp']}"
    )

    current_by_sector = {}

    for row in current_snapshot["rows"]:

        sektor = row.get(
            "Sektor",
            ""
        ).strip()

        if sektor:

            current_by_sector[sektor] = row

    previous_by_sector = {}

    for row in previous_snapshot["rows"]:

        sektor = row.get(
            "Sektor",
            ""
        ).strip()

        if sektor:

            previous_by_sector[sektor] = row

    sectors = sorted(
        set(current_by_sector.keys())
        |
        set(previous_by_sector.keys())
    )

    print("\n" + "-" * 70)

    for sector in sectors:

        current = current_by_sector.get(
            sector
        )

        previous = previous_by_sector.get(
            sector
        )

        print(
            f"\nSektor : {sector}"
        )

        if not current:

            print(
                f"  Tidak ada pada "
                f"{current_month}"
            )

            print(
                f"  Kandidat sebelumnya : "
                f"{previous.get('Nama', '-')}"
            )

            continue

        if not previous:

            print(
                f"  Kandidat baru pada "
                f"{current_month}"
            )

            print(
                f"  Kandidat sekarang : "
                f"{current.get('Nama', '-')}"
            )

            continue

        previous_name = previous.get(
            "Nama",
            "-"
        ).strip()

        current_name = current.get(
            "Nama",
            "-"
        ).strip()

        print(
            f"  Sebelumnya : {previous_name}"
        )

        print(
            f"  Sekarang   : {current_name}"
        )

        if previous_name != current_name:

            print(
                "  Kandidat berubah : YA"
            )

        else:

            print(
                "  Kandidat berubah : TIDAK"
            )

        try:

            previous_score = float(
                previous.get(
                    "Score",
                    "0"
                )
            )

            current_score = float(
                current.get(
                    "Score",
                    "0"
                )
            )

            score_change = (
                current_score
                -
                previous_score
            )

            if score_change > 0:

                change_text = (
                    f"+{score_change:g}"
                )

            else:

                change_text = (
                    f"{score_change:g}"
                )

            print(
                f"  Score sebelumnya : "
                f"{previous_score:g}"
            )

            print(
                f"  Score sekarang   : "
                f"{current_score:g}"
            )

            print(
                f"  Perubahan Score  : "
                f"{change_text}"
            )

        except (
            ValueError,
            TypeError
        ):

            print(
                "  Perubahan Score  : -"
            )

    print("\n" + "-" * 70)

    print(
        "Catatan:"
    )

    print(
        "- Perbandingan menggunakan "
        "snapshot terakhir setiap bulan."
    )

    print(
        "- Tidak ada ranking lintas sektor."
    )

    print(
        "- V5.6 bukan perintah beli/jual."
    )
    show_monthly_comparison()
# ============================================================
# RINGKASAN PERINGATAN
# ============================================================


# ============================================================
# RINGKASAN
# ============================================================

print("\n")
print("=" * 70)
print("RINGKASAN")
print("=" * 70)

fund_count = sum(
    1 for c in candidates
    if c["type"] == "REKSA DANA"
)

stock_count = sum(
    1 for c in candidates
    if c["type"] == "SAHAM"
)

print(
    f"Reksa dana berhasil diproses : "
    f"{fund_count}/1"
)

print(
    f"Sektor saham berhasil diproses: "
    f"{stock_count}/4"
)

print(
    f"Total kandidat                : "
    f"{len(candidates)}/5"
)

if fund_count == 1 and stock_count == 4:

    print(
        "Status : SEMUA KOMPONEN BERHASIL"
    )

else:

    print(
        "Status : ADA KOMPONEN YANG PERLU DIPERIKSA"
    )


# ============================================================
# CEK DUPLIKASI SAHAM
# ============================================================

stock_codes = [
    candidate["code"]
    for candidate in candidates
    if candidate["type"] == "SAHAM"
]

duplicates = set(
    code
    for code in stock_codes
    if stock_codes.count(code) > 1
)

print("\n")
print("=" * 70)
print("CEK DUPLIKASI SAHAM")
print("=" * 70)

if duplicates:

    print(
        "PERINGATAN: Ada saham yang muncul "
        "di lebih dari satu sektor:"
    )

    for code in duplicates:

        print(f"- {code}")

else:

    print(
        "OK: Tidak ada saham yang terduplikasi."
    )


# ============================================================
# SIMPAN HISTORY
# ============================================================

if len(candidates) > 0:

    save_history(candidates)

    print("\n")
    print("=" * 70)
    print("RIWAYAT SCREENING")
    print("=" * 70)

    print(
        f"Data berhasil disimpan ke: "
        f"{HISTORY_FILE}"
    )

    # ========================================================
    # GENERATE LAPORAN V5.5
    # ========================================================

    print("\n")
    print("=" * 70)
    print("GENERATE LAPORAN V5.5")
    print("=" * 70)

    try:

        result = subprocess.run(
            [sys.executable, "generate_report_v55.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            print(
                 "OK: Laporan V5.5 berhasil dibuat."
            )

            print(
                "File: laporan_screening_v55.txt"
            )

        else:

            print(
                "PERINGATAN: Generator laporan gagal."
            )

            if result.stderr:
                print(result.stderr)

    except Exception as e:

        print(
            f"PERINGATAN: Tidak dapat menjalankan "
            f"generator laporan: {e}"
        )

# ============================================================
# CATATAN
# ============================================================

print("\n")
print("=" * 70)
print("CATATAN")
print("=" * 70)

print(
    "Score antar sektor tidak digunakan untuk "
    "ranking keseluruhan."
)

print(
    "Setiap sektor menggunakan aturan screening "
    "yang berbeda."
)

print(
    "History digunakan untuk melihat perubahan kandidat, "
    "skor, tanggal data, dan sumber data dari waktu ke waktu."
)

print(
    "Hasil screening bukan perintah otomatis "
    "untuk membeli saham."
)

print(
    "Data fundamental, valuasi, dan data reksa "
    "dana perlu diperiksa kembali sebelum mengambil "
    "keputusan investasi."
)


print("\n")
print("=" * 70)
print("           MASTER STOCK AGENT V5 SELESAI")
print("=" * 70)

input("\nTekan ENTER untuk keluar...")
