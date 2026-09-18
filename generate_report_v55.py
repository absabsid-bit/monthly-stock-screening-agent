import csv
import os


HISTORY_FILE = "screening_history.csv"
REPORT_FILE = "laporan_screening_v55.txt"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        print(f"ERROR: {HISTORY_FILE} tidak ditemukan.")
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        return list(reader)


def get_latest_snapshot(rows):
    if not rows:
        return []

    timestamps = []

    for row in rows:
        tanggal = row.get("Tanggal", "").strip()
        waktu = row.get("Waktu", "").strip()

        if tanggal and waktu:
            timestamps.append(f"{tanggal} {waktu}")

    if not timestamps:
        return []

    latest_timestamp = max(timestamps)

    latest_rows = []

    for row in rows:
        timestamp = (
            f"{row.get('Tanggal', '').strip()} "
            f"{row.get('Waktu', '').strip()}"
        )

        if timestamp == latest_timestamp:
            latest_rows.append(row)

    return latest_rows
def get_previous_snapshot(rows):
    if not rows:
        return []

    timestamps = []

    for row in rows:
        tanggal = row.get("Tanggal", "").strip()
        waktu = row.get("Waktu", "").strip()

        if tanggal and waktu:
            timestamps.append(f"{tanggal} {waktu}")

    unique_timestamps = sorted(set(timestamps), reverse=True)

    if len(unique_timestamps) < 2:
        return []

    previous_timestamp = unique_timestamps[1]

    previous_rows = []

    for row in rows:
        timestamp = (
            f"{row.get('Tanggal', '').strip()} "
            f"{row.get('Waktu', '').strip()}"
        )

        if timestamp == previous_timestamp:
            previous_rows.append(row)

    return previous_rows

def format_score(row):
    score = row.get("Score", "-").strip()
    maximum = row.get("MaximumScore", "-").strip()
    percent = row.get("ScorePercent", "-").strip()

    return f"{score}/{maximum} ({percent}%)"

# ============================================================
# V5.6 - SNAPSHOT BULANAN
# ============================================================

def get_monthly_snapshots(rows):

    from collections import defaultdict

    monthly_data = defaultdict(list)

    for row in rows:

        tanggal = row.get("Tanggal", "").strip()
        waktu = row.get("Waktu", "").strip()

        if not tanggal or not waktu:
            continue

        bulan = tanggal[:7]
        timestamp = f"{tanggal} {waktu}"

        monthly_data[bulan].append(
            {
                "timestamp": timestamp,
                "row": row
            }
        )

    monthly_snapshots = {}

    for bulan, records in monthly_data.items():

        records.sort(
            key=lambda x: x["timestamp"]
        )

        latest_timestamp = records[-1]["timestamp"]

        snapshot_rows = []

        for record in records:

            if record["timestamp"] == latest_timestamp:

                snapshot_rows.append(
                    record["row"]
                )

        monthly_snapshots[bulan] = {
            "timestamp": latest_timestamp,
            "rows": snapshot_rows
        }

    return monthly_snapshots


def build_monthly_comparison(rows):

    lines = []

    lines.append("")
    lines.append("-" * 70)
    lines.append("PERBANDINGAN BULANAN V5.6")
    lines.append("-" * 70)

    monthly_snapshots = get_monthly_snapshots(rows)

    if not monthly_snapshots:

        lines.append(
            "Belum ada data screening bulanan."
        )

        return lines

    months = sorted(
        monthly_snapshots.keys(),
        reverse=True
    )

    current_month = months[0]

    lines.append(
        f"Bulan terbaru : {current_month}"
    )

    if len(months) < 2:

        lines.append(
            "Belum ada bulan sebelumnya untuk dibandingkan."
        )

        lines.append(
            "Minimal diperlukan data dari 2 bulan berbeda."
        )

        return lines

    previous_month = months[1]

    current_snapshot = (
        monthly_snapshots[current_month]
    )

    previous_snapshot = (
        monthly_snapshots[previous_month]
    )

    lines.append(
        f"Bulan sebelumnya : {previous_month}"
    )

    lines.append("")

    lines.append(
        f"Snapshot terbaru    : "
        f"{current_snapshot['timestamp']}"
    )

    lines.append(
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

    lines.append("")

    for sector in sectors:

        current = current_by_sector.get(
            sector
        )

        previous = previous_by_sector.get(
            sector
        )

        lines.append(
            f"{sector:<30}:"
        )

        if not current:

            lines.append(
                f"  Tidak ada pada {current_month}"
            )

            lines.append(
                f"  Kandidat sebelumnya : "
                f"{previous.get('Nama', '-')}"
            )

            lines.append("")

            continue

        if not previous:

            lines.append(
                f"  Kandidat baru pada {current_month}"
            )

            lines.append(
                f"  Kandidat sekarang : "
                f"{current.get('Nama', '-')}"
            )

            lines.append("")

            continue

        previous_name = previous.get(
            "Nama",
            "-"
        ).strip()

        current_name = current.get(
            "Nama",
            "-"
        ).strip()

        lines.append(
            f"  Sebelumnya : {previous_name}"
        )

        lines.append(
            f"  Sekarang   : {current_name}"
        )

        if previous_name != current_name:

            lines.append(
                "  Kandidat berubah : YA"
            )

        else:

            lines.append(
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

            lines.append(
                f"  Score sebelumnya : "
                f"{previous_score:g}"
            )

            lines.append(
                f"  Score sekarang   : "
                f"{current_score:g}"
            )

            lines.append(
                f"  Perubahan Score  : "
                f"{change_text}"
            )

        except (
            ValueError,
            TypeError
        ):

            lines.append(
                "  Perubahan Score  : -"
            )

        lines.append("")

    lines.append(
        "Catatan:"
    )

    lines.append(
        "- Menggunakan snapshot terakhir setiap bulan."
    )

    lines.append(
        "- Tidak menggunakan ranking lintas sektor."
    )

    lines.append(
        "- Bukan perintah otomatis untuk membeli atau menjual."
    )

    return lines
# ============================================================
# V5.7 - TREN MULTI-BULAN
# ============================================================

def build_multi_month_trend(rows, number_of_months=3):

    lines = []

    lines.append("")
    lines.append("-" * 70)
    lines.append("TREN MULTI-BULAN V5.7")
    lines.append("-" * 70)

    monthly_snapshots = get_monthly_snapshots(rows)

    if not monthly_snapshots:

        lines.append(
            "Belum ada data screening bulanan."
        )

        return lines

    months = sorted(
        monthly_snapshots.keys(),
        reverse=True
    )

    if len(months) < number_of_months:

        lines.append(
            f"Data belum cukup untuk analisis "
            f"{number_of_months} bulan."
        )

        lines.append(
            f"Data bulan tersedia : {len(months)}"
        )

        lines.append(
            f"Minimal diperlukan  : {number_of_months}"
        )

        return lines

    selected_months = months[
        :number_of_months
    ]

    selected_months.reverse()

    lines.append(
        f"Periode analisis : "
        f"{selected_months[0]} "
        f"-> "
        f"{selected_months[-1]}"
    )

    lines.append(
        f"Jumlah bulan    : "
        f"{len(selected_months)}"
    )

    lines.append("")

    sector_data = {}

    for month in selected_months:

        snapshot = monthly_snapshots[month]

        for row in snapshot["rows"]:

            sector = row.get(
                "Sektor",
                ""
            ).strip()

            if not sector:
                continue

            if sector not in sector_data:

                sector_data[sector] = {}

            sector_data[sector][month] = row

    for sector in sorted(sector_data.keys()):

        lines.append(
            f"{sector}"
        )

        lines.append(
            "-" * 70
        )

        month_records = []

        for month in selected_months:

            row = sector_data[sector].get(
                month
            )

            if not row:

                lines.append(
                    f"  {month} : "
                    "Tidak ada data"
                )

                continue

            name = row.get(
                "Nama",
                "-"
            ).strip()

            score_text = row.get(
                "Score",
                "-"
            ).strip()

            lines.append(
                f"  {month} : "
                f"{name} | Score {score_text}"
            )

            try:

                score = float(score_text)

                month_records.append(
                    {
                        "month": month,
                        "name": name,
                        "score": score
                    }
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        if len(month_records) >= 2:

            first = month_records[0]
            last = month_records[-1]

            score_change = (
                last["score"]
                -
                first["score"]
            )

            if score_change > 0:

                trend = "NAIK"
                change_text = (
                    f"+{score_change:g}"
                )

            elif score_change < 0:

                trend = "TURUN"
                change_text = (
                    f"{score_change:g}"
                )

            else:

                trend = "TETAP"
                change_text = "0"

            lines.append("")

            lines.append(
                f"  Tren Score : {trend}"
            )

            lines.append(
                f"  Perubahan Score "
                f"({first['month']} -> "
                f"{last['month']}) : "
                f"{change_text}"
            )

            if first["name"] != last["name"]:

                lines.append(
                    "  Perubahan Kandidat : YA"
                )

                lines.append(
                    f"  Kandidat awal  : "
                    f"{first['name']}"
                )

                lines.append(
                    f"  Kandidat akhir : "
                    f"{last['name']}"
                )

            else:

                lines.append(
                    "  Perubahan Kandidat : TIDAK"
                )

        lines.append("")

    lines.append(
        "Catatan:"
    )

    lines.append(
        "- Tren dihitung berdasarkan "
        "snapshot terakhir setiap bulan."
    )

    lines.append(
        "- V5.7 tidak memberikan ranking "
        "lintas sektor."
    )

    lines.append(
        "- Tren bukan prediksi harga saham."
    )

    lines.append(
        "- Hasil bukan perintah otomatis "
        "untuk membeli atau menjual."
    )

    return lines
def build_report(rows):
    latest = get_latest_snapshot(rows)
    previous = get_previous_snapshot(rows)

    if not latest:
        return "Tidak ada data screening yang dapat digunakan."

    latest_timestamp = (
        f"{latest[0].get('Tanggal', '-')}"
        f" {latest[0].get('Waktu', '-')}"
    )

    previous_timestamp = "-"

    if previous:
        previous_timestamp = (
            f"{previous[0].get('Tanggal', '-')}"
            f" {previous[0].get('Waktu', '-')}"
        )

    lines = []

    lines.append("=" * 70)
    lines.append("LAPORAN SCREENING V5.5")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Tanggal screening : {latest_timestamp}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("HASIL SCREENING")
    lines.append("-" * 70)

    for row in latest:

        jenis = row.get("Jenis", "-").strip()
        sektor = row.get("Sektor", "-").strip()
        kode = row.get("Kode", "-").strip()
        nama = row.get("Nama", "-").strip()
        score = format_score(row)
        status = row.get("Status", "-").strip()
        tanggal_data = row.get("TanggalData", "-").strip()
        sumber = row.get("Sumber", "-").strip()

        lines.append("")
        lines.append(f"Jenis       : {jenis}")
        lines.append(f"Sektor      : {sektor}")

        if kode and kode != "-":
            lines.append(f"Kode        : {kode}")

        lines.append(f"Kandidat    : {nama}")
        lines.append(f"Score       : {score}")
        lines.append(f"Status      : {status}")
        lines.append(f"Tanggal Data: {tanggal_data}")
        lines.append(f"Sumber      : {sumber}")

        if jenis == "SAHAM":

            component_fields = [
                ("ROE", "Score_ROE"),
                ("Pertumbuhan laba", "Score_Profit"),
                ("Pertumbuhan revenue", "Score_Revenue"),
                ("Pertumbuhan equity", "Score_Equity"),
                ("Konsistensi laba", "Score_Consistency"),
                ("PER", "Score_PER"),
                ("PBV", "Score_PBV"),
            ]

            has_component = False

            for label, field in component_fields:
                value = row.get(field, "-").strip()

                if value == "0":
                    value = "-"

                if value != "-":
                    if not has_component:
                        lines.append("")
                        lines.append("Component Score:")

                    lines.append(f"  {label:<22}: {value}")
                    has_component = True

    lines.append("")
    lines.append("-" * 70)
    lines.append("RINGKASAN")
    lines.append("-" * 70)

    funds = [
        row for row in latest
        if row.get("Jenis", "").strip() == "REKSA DANA"
    ]

    stocks = [
        row for row in latest
        if row.get("Jenis", "").strip() == "SAHAM"
    ]

    passed = [
        row for row in latest
        if row.get("Status", "").strip() == "LULUS"
    ]

    lines.append(f"Reksa dana diproses : {len(funds)}")
    lines.append(f"Saham diproses      : {len(stocks)}")
    lines.append(f"Total kandidat      : {len(latest)}")
    lines.append(f"Status LULUS        : {len(passed)}/{len(latest)}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("PERBANDINGAN DENGAN SCREENING SEBELUMNYA")
    lines.append("-" * 70)

    if previous:
        lines.append(f"Screening sebelumnya : {previous_timestamp}")
        lines.append("")

        previous_map = {}

        for row in previous:
            sektor = row.get("Sektor", "").strip()

            if sektor:
                previous_map[sektor] = row

        for row in latest:
            sektor = row.get("Sektor", "").strip()
            nama = row.get("Nama", "-").strip()

            old = previous_map.get(sektor)

            if not old:
                lines.append(f"{sektor:<30}: Kandidat baru")
                lines.append(f"  Sekarang : {nama}")
                continue

            old_name = old.get("Nama", "-").strip()

            try:
                current_score = float(row.get("Score", "0"))
                old_score = float(old.get("Score", "0"))
                score_change = current_score - old_score

                if score_change > 0:
                    change_text = f"+{score_change:g}"
                else:
                    change_text = f"{score_change:g}"

            except (ValueError, TypeError):
                change_text = "-"

            lines.append(f"{sektor:<30}:")
            lines.append(f"  Sebelumnya : {old_name}")
            lines.append(f"  Sekarang   : {nama}")
            lines.append(f"  Perubahan Score : {change_text}")
            if row.get("Jenis", "").strip() == "SAHAM":
                component_fields = [
                    ("ROE", "Score_ROE"),
                    ("Pertumbuhan laba", "Score_Profit"),
                    ("Pertumbuhan revenue", "Score_Revenue"),
                    ("Pertumbuhan equity", "Score_Equity"),
                    ("Konsistensi laba", "Score_Consistency"),
                    ("PER", "Score_PER"),
                    ("PBV", "Score_PBV"),
                ]

                component_changes = []

                for label, field in component_fields:

                    current_value = row.get(field, "-").strip()
                    old_value = old.get(field, "-").strip()

                    if current_value == "0":
                        current_value = "-"

                    if old_value == "0":
                        old_value = "-"

                    if current_value == "-" or old_value == "-":
                        continue

                    try:
                        current_value_num = float(current_value)
                        old_value_num = float(old_value)
                        change = current_value_num - old_value_num

                        if change > 0:
                            change_text = f"+{change:g}"
                        else:
                            change_text = f"{change:g}"

                        component_changes.append(
                            (
                                label,
                                old_value_num,
                                current_value_num,
                                change_text
                            )
                        )

                    except (ValueError, TypeError):
                        continue

                if component_changes:
                    lines.append("")
                    lines.append("  Component Score:")

                    for (
                        label,
                        old_value_num,
                        current_value_num,
                        change_text
                    ) in component_changes:

                        lines.append(
                            f"    {label:<20}: "
                            f"{old_value_num:g} -> "
                            f"{current_value_num:g} "
                            f"({change_text})"
                        )
    else:
        lines.append("Belum ada screening sebelumnya untuk dibandingkan.")
    # V5.6 - PERBANDINGAN BULANAN
    monthly_lines = build_monthly_comparison(rows)

    lines.extend(monthly_lines)

    # V5.7 - TREN MULTI-BULAN
    trend_lines = build_multi_month_trend(rows)

    lines.extend(trend_lines)

   
   
    lines.append("")
    lines.append("-" * 70)
    lines.append("CATATAN")
    lines.append("-" * 70)
    lines.append(
        "Laporan ini merupakan ringkasan hasil screening "
        "berdasarkan data yang tersimpan."
    )
    lines.append(
        "Score antar sektor tidak digunakan sebagai ranking global."
    )
    lines.append(
        "Laporan bukan perintah otomatis untuk membeli atau menjual."
    )
    lines.append(
        "Data fundamental dan kondisi pasar tetap perlu diperiksa "
        "sebelum mengambil keputusan investasi."
    )

    lines.append("")
    lines.append("=" * 70)
    lines.append("SELESAI")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():

    rows = load_history()

    if not rows:
        return

    report = build_report(rows)

    print("")
    print(report)

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    print("")
    print("=" * 70)
    print(f"Laporan berhasil disimpan ke: {REPORT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()