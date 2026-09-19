import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Stock Agent Dashboard",
    page_icon="📊",
    layout="wide"
)
# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #f8fafc;
    }

    /* Main content */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Main title */
    h1 {
        font-size: 2.4rem !important;
        font-weight: 700 !important;
    }

    /* Section headers */
    h2 {
        margin-top: 1rem !important;
        font-weight: 650 !important;
    }

    h3 {
        font-weight: 600 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    /* Information boxes */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    /* Sidebar title */
    section[data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)
HISTORY_FILE = "screening_history.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv(
        HISTORY_FILE,
        encoding="utf-8-sig"
    )

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce"
    )

    df["Waktu"] = df["Waktu"].astype(str)

    df["TanggalWaktu"] = pd.to_datetime(
        df["Tanggal"].dt.strftime("%Y-%m-%d")
        + " "
        + df["Waktu"],
        errors="coerce"
    )

    df["Score"] = pd.to_numeric(
        df["Score"],
        errors="coerce"
    )

    df["MaximumScore"] = pd.to_numeric(
        df["MaximumScore"],
        errors="coerce"
    )

    df["ScorePercent"] = pd.to_numeric(
        df["ScorePercent"],
        errors="coerce"
    )

    df["Bulan"] = (
        df["Tanggal"]
        .dt.to_period("M")
        .astype(str)
    )

    return df
# ============================================================
# LOAD HISTORY
# ============================================================

try:
    df = load_data()

except FileNotFoundError:
    st.error("❌ screening_history.csv tidak ditemukan.")
    st.stop()

if df.empty:
    st.warning("Belum ada data screening.")
    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("📊 Stock Agent Dashboard")

st.caption(
    "Monitoring • Historical Analysis • Alert • Monthly Trend"
)

st.subheader("Monthly Stock & Mutual Fund Screening")

st.write(
    "Monitoring hasil screening saham dan reksa dana "
    "berdasarkan historical screening."
)


# ============================================================
# SIDEBAR FILTER
# ============================================================

st.sidebar.title("📊 Stock Agent")

st.sidebar.caption(
    "Monthly Stock & Mutual Fund Screening"
)

st.sidebar.divider()

st.sidebar.header("🔎 Filter")

# -----------------------------
# Filter jenis
# -----------------------------

jenis_list = sorted(
    df["Jenis"].dropna().unique().tolist()
)

jenis_filter = st.sidebar.multiselect(
    "Jenis",
    jenis_list,
    default=jenis_list
)

filtered_df = df[
    df["Jenis"].isin(jenis_filter)
].copy()


# -----------------------------
# Filter sektor
# -----------------------------

sektor_list = sorted(
    filtered_df["Sektor"].dropna().unique().tolist()
)

sektor_filter = st.sidebar.multiselect(
    "Sektor",
    sektor_list,
    default=sektor_list
)

filtered_df = filtered_df[
    filtered_df["Sektor"].isin(sektor_filter)
].copy()


# -----------------------------
# Filter kandidat
# -----------------------------

candidate_names = sorted(
    filtered_df["Nama"].dropna().unique().tolist()
)

candidate_filter = st.sidebar.multiselect(
    "Kandidat",
    candidate_names
)

if candidate_filter:
    filtered_df = filtered_df[
        filtered_df["Nama"].isin(candidate_filter)
    ].copy()


# ============================================================
# LATEST SCREENING
# ============================================================

latest_datetime = filtered_df["TanggalWaktu"].max()

latest_df = filtered_df[
    filtered_df["TanggalWaktu"] == latest_datetime
].copy()

# ============================================================
# METRICS
# ============================================================

fund_count = len(
    latest_df[
        latest_df["Jenis"].str.upper() == "REKSA DANA"
    ]
)

stock_count = len(
    latest_df[
        latest_df["Jenis"].str.upper() == "SAHAM"
    ]
)

passed_count = len(
    latest_df[
        latest_df["Status"].str.upper() == "LULUS"
    ]
)

total_count = len(latest_df)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📅 Screening Terakhir",
        latest_datetime.strftime("%d/%m/%y")
    )
with col2:
    st.metric(
        "💰 Reksa Dana",
        fund_count
    )

with col3:
    st.metric(
        "📈 Saham",
        stock_count
    )

with col4:
    st.metric(
        "✅ Lulus",
        f"{passed_count}/{total_count}"
    )


# ============================================================
# LATEST CANDIDATES
# ============================================================

st.divider()

st.header("🎯 Kandidat Screening Terbaru")

display_columns = [
    "Jenis",
    "Sektor",
    "Kode",
    "Nama",
    "Score",
    "MaximumScore",
    "ScorePercent",
    "Status"
]

available_columns = [
    col for col in display_columns
    if col in latest_df.columns
]

candidate_table = latest_df[
    available_columns
].copy()

st.dataframe(
    candidate_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SCORE CHART
# ============================================================

st.divider()

st.header("📊 Score Kandidat Terbaru")

chart_df = latest_df.copy()

chart_df["Label"] = chart_df.apply(
    lambda row:
    row["Kode"]
    if pd.notna(row["Kode"]) and str(row["Kode"]) != "-"
    else row["Nama"],
    axis=1
)

fig = px.bar(
    chart_df,
    x="Label",
    y="Score",
    text="Score",
    hover_data=[
        "Nama",
        "Sektor",
        "MaximumScore",
        "Status"
    ],
    title="Score Screening Terbaru"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    xaxis_title="Kandidat",
    yaxis_title="Score",
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# MONTHLY SCORE TREND
# ============================================================

st.divider()

st.header("📈 Perkembangan Score Bulanan")

if filtered_df["Bulan"].nunique() < 2:

    st.info(
        "Data belum cukup untuk menampilkan "
        "perkembangan antar-bulan. "
        "Minimal diperlukan data dari 2 bulan berbeda."
    )

else:

    trend_df = (
        filtered_df
        .sort_values("Tanggal")
        .groupby(
            ["Bulan", "Sektor", "Nama"],
            as_index=False
        )
        .last()
    )

    fig_trend = px.line(
        trend_df,
        x="Bulan",
        y="Score",
        color="Nama",
        markers=True,
        hover_data=[
            "Sektor",
            "MaximumScore",
            "Status"
        ],
        title="Trend Score Bulanan"
    )

    fig_trend.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Score",
        height=500
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )


# ============================================================
# HISTORICAL DATA
# ============================================================

st.divider()

st.header("📚 Riwayat Screening")

history_columns = [
    "Tanggal",
    "Jenis",
    "Sektor",
    "Kode",
    "Nama",
    "Score",
    "MaximumScore",
    "ScorePercent",
    "Status"
]

available_history_columns = [
    col for col in history_columns
    if col in filtered_df.columns
]

history_table = (
    filtered_df[
        available_history_columns
    ]
    .sort_values("Tanggal", ascending=False)
)

st.dataframe(
    history_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# COMPONENT ANALYSIS
# ============================================================

st.divider()

st.header("🔬 Component Analysis")

st.write(
    "Analisis komponen score berdasarkan hasil screening "
    "historical."
)

# Hanya saham yang mempunyai component score
stock_component_df = filtered_df[
    filtered_df["Jenis"].astype(str).str.upper() == "SAHAM"
].copy()

if stock_component_df.empty:

    st.info(
        "Tidak ada data saham untuk Component Analysis."
    )

else:

    # Kandidat saham
    component_candidates = sorted(
        stock_component_df["Nama"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_component = st.selectbox(
        "Pilih Kandidat Saham",
        component_candidates
    )

    selected_df = stock_component_df[
        stock_component_df["Nama"] == selected_component
    ].copy()

    # Ambil screening terbaru kandidat
    selected_latest_datetime = selected_df[
        "TanggalWaktu"
    ].max()

    selected_latest = selected_df[
        selected_df["TanggalWaktu"]
        == selected_latest_datetime
    ].iloc[0]

    # Component score
    component_data = {
        "ROE": (
            selected_latest.get("Score_ROE"),
            20
        ),
        "Pertumbuhan Laba": (
            selected_latest.get("Score_Profit"),
            15
        ),
        "Pertumbuhan Revenue": (
            selected_latest.get("Score_Revenue"),
            10
        ),
        "Pertumbuhan Equity": (
            selected_latest.get("Score_Equity"),
            10
        ),
        "Konsistensi Laba": (
            selected_latest.get("Score_Consistency"),
            15
        ),
        "PER": (
            selected_latest.get("Score_PER"),
            15
        ),
        "PBV": (
            selected_latest.get("Score_PBV"),
            15
        )
    }

    component_rows = []

    for name, values in component_data.items():

        score = values[0]
        maximum = values[1]

        try:
            score = int(score)
        except (ValueError, TypeError):
            continue

        component_rows.append({
            "Komponen": name,
            "Score": score,
            "Maximum": maximum,
            "Persentase": round(
                score / maximum * 100,
                1
            )
        })

    if not component_rows:

        st.warning(
            "Component score belum tersedia untuk kandidat ini."
        )

    else:

        component_chart_df = pd.DataFrame(
            component_rows
        )

        # -----------------------------
        # Candidate summary
        # -----------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Kandidat",
                selected_latest["Kode"]
            )

        with col2:
            st.metric(
                "Total Score",
                f"{int(selected_latest['Score'])}/"
                f"{int(selected_latest['MaximumScore'])}"
            )

        with col3:
            st.metric(
                "Status",
                selected_latest["Status"]
            )

        # -----------------------------
        # Component table
        # -----------------------------

        st.subheader("📋 Detail Component Score")

        st.dataframe(
            component_chart_df,
            use_container_width=True,
            hide_index=True
        )

        # -----------------------------
        # Component bar chart
        # -----------------------------

        st.subheader("📊 Component Score")

        fig_component = px.bar(
            component_chart_df,
            x="Komponen",
            y="Score",
            text="Score",
            hover_data=[
                "Maximum",
                "Persentase"
            ],
            title=f"Component Score — {selected_latest['Kode']}"
        )

        fig_component.update_traces(
            textposition="outside"
        )

        fig_component.update_layout(
            yaxis_title="Score",
            xaxis_title="Komponen",
            yaxis=dict(
                range=[
                    0,
                    max(component_chart_df["Maximum"]) + 3
                ]
            ),
            height=500
        )

        st.plotly_chart(
            fig_component,
            use_container_width=True
        )
# ============================================================
# ALERT DASHBOARD
# ============================================================

st.divider()

st.header("🚨 Alert Monitoring")

st.write(
    "Perbandingan screening terbaru dengan snapshot "
    "screening sebelumnya."
)

# ------------------------------------------------------------
# Cari snapshot terbaru dan sebelumnya
# ------------------------------------------------------------

valid_history = filtered_df.dropna(
    subset=["TanggalWaktu"]
).copy()

unique_snapshots = sorted(
    valid_history["TanggalWaktu"].unique()
)

if len(unique_snapshots) < 2:

    st.info(
        "Belum ada snapshot sebelumnya untuk dibandingkan. "
        "Minimal diperlukan 2 kali screening."
    )

else:

    latest_snapshot = unique_snapshots[-1]
    previous_snapshot = unique_snapshots[-2]

    current_snapshot_df = valid_history[
        valid_history["TanggalWaktu"] == latest_snapshot
    ].copy()

    previous_snapshot_df = valid_history[
        valid_history["TanggalWaktu"] == previous_snapshot
    ].copy()

    alerts = []

    # --------------------------------------------------------
    # Bandingkan berdasarkan sektor
    # --------------------------------------------------------

    sectors = sorted(
        set(
            current_snapshot_df["Sektor"].dropna()
        ).intersection(
            set(
                previous_snapshot_df["Sektor"].dropna()
            )
        )
    )

    for sector in sectors:

        current_sector = current_snapshot_df[
            current_snapshot_df["Sektor"] == sector
        ]

        previous_sector = previous_snapshot_df[
            previous_snapshot_df["Sektor"] == sector
        ]

        if current_sector.empty or previous_sector.empty:
            continue

        current_row = current_sector.iloc[0]
        previous_row = previous_sector.iloc[0]

        # ----------------------------------------------------
        # Identitas kandidat
        # ----------------------------------------------------

        if str(current_row["Jenis"]).upper() == "SAHAM":

            current_identifier = str(
                current_row["Kode"]
            ).strip()

            previous_identifier = str(
                previous_row["Kode"]
            ).strip()

        else:

            current_identifier = str(
                current_row["Nama"]
            ).strip()

            previous_identifier = str(
                previous_row["Nama"]
            ).strip()

        # ----------------------------------------------------
        # Alert kandidat berubah
        # ----------------------------------------------------

        if current_identifier != previous_identifier:

            alerts.append({
                "type": "candidate",
                "sector": sector,
                "name": current_row["Nama"],
                "message": (
                    f"{previous_identifier} → "
                    f"{current_identifier}"
                )
            })

        # ----------------------------------------------------
        # Alert total score turun
        # ----------------------------------------------------

        try:

            current_score = float(
                current_row["Score"]
            )

            previous_score = float(
                previous_row["Score"]
            )

            score_change = (
                current_score - previous_score
            )

            if score_change < 0:

                alerts.append({
                    "type": "score",
                    "sector": sector,
                    "name": current_row["Nama"],
                    "message": (
                        f"{previous_score:g} → "
                        f"{current_score:g} "
                        f"({score_change:g})"
                    )
                })

        except (
            ValueError,
            TypeError
        ):
            pass

        # ----------------------------------------------------
        # Component score
        # Hanya untuk saham
        # ----------------------------------------------------

        if str(current_row["Jenis"]).upper() != "SAHAM":
            continue

        component_names = {
            "Score_ROE": "ROE",
            "Score_Profit": "Pertumbuhan Laba",
            "Score_Revenue": "Pertumbuhan Revenue",
            "Score_Equity": "Pertumbuhan Equity",
            "Score_Consistency": "Konsistensi Laba",
            "Score_PER": "PER",
            "Score_PBV": "PBV"
        }

        for column, label in component_names.items():

            if column not in current_row.index:
                continue

            if column not in previous_row.index:
                continue

            try:

                current_component = int(
                    current_row[column]
                )

                previous_component = int(
                    previous_row[column]
                )

            except (
                ValueError,
                TypeError
            ):
                continue

            component_change = (
                current_component
                - previous_component
            )

            if component_change < 0:

                alerts.append({
                    "type": "component",
                    "sector": sector,
                    "name": current_row["Nama"],
                    "component": label,
                    "message": (
                        f"{previous_component} → "
                        f"{current_component} "
                        f"({component_change})"
                    )
                })

    # --------------------------------------------------------
    # Tampilkan informasi snapshot
    # --------------------------------------------------------

    st.caption(
        "Snapshot terbaru: "
        + pd.Timestamp(latest_snapshot).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    st.caption(
        "Snapshot sebelumnya: "
        + pd.Timestamp(previous_snapshot).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    # --------------------------------------------------------
    # Tampilkan alert
    # --------------------------------------------------------

    if not alerts:

        st.success(
            "✅ Tidak ada alert. "
            "Tidak ditemukan penurunan score, "
            "penurunan component score, atau perubahan kandidat."
        )

    else:

        st.warning(
            f"⚠️ Ditemukan {len(alerts)} perubahan "
            "yang perlu diperiksa."
        )

        # ----------------------------------------------------
        # Kandidat berubah
        # ----------------------------------------------------

        candidate_alerts = [
            alert for alert in alerts
            if alert["type"] == "candidate"
        ]

        if candidate_alerts:

            st.subheader("🔄 Kandidat Berubah")

            for alert in candidate_alerts:

                st.error(
                    f"**{alert['sector']}** — "
                    f"{alert['message']}"
                )

        # ----------------------------------------------------
        # Score turun
        # ----------------------------------------------------

        score_alerts = [
            alert for alert in alerts
            if alert["type"] == "score"
        ]

        if score_alerts:

            st.subheader("📉 Score Total Turun")

            for alert in score_alerts:

                st.error(
                    f"**{alert['sector']} — "
                    f"{alert['name']}**  \n"
                    f"Score: {alert['message']}"
                )

        # ----------------------------------------------------
        # Component turun
        # ----------------------------------------------------

        component_alerts = [
            alert for alert in alerts
            if alert["type"] == "component"
        ]

        if component_alerts:

            st.subheader("⚠️ Component Score Turun")

            component_table = pd.DataFrame(
                [
                    {
                        "Sektor": alert["sector"],
                        "Kandidat": alert["name"],
                        "Komponen": alert["component"],
                        "Perubahan": alert["message"]
                    }
                    for alert in component_alerts
                ]
            )

            st.dataframe(
                component_table,
                use_container_width=True,
                hide_index=True
            )
# ============================================================
# MONTHLY ANALYSIS
# ============================================================

st.divider()

st.header("📅 Monthly Analysis")

st.write(
    "Analisis perkembangan hasil screening berdasarkan "
    "snapshot terbaru pada setiap bulan."
)

monthly_source = filtered_df.dropna(
    subset=["TanggalWaktu"]
).copy()

if monthly_source.empty:

    st.info(
        "Belum ada data yang dapat dianalisis."
    )

else:

    # --------------------------------------------------------
    # Ambil snapshot terakhir setiap bulan
    # --------------------------------------------------------

    monthly_latest_times = (
        monthly_source
        .groupby("Bulan")["TanggalWaktu"]
        .max()
        .reset_index()
    )

    monthly_snapshots = monthly_source.merge(
        monthly_latest_times,
        on=["Bulan", "TanggalWaktu"],
        how="inner"
    )

    monthly_snapshots = (
        monthly_snapshots
        .sort_values("TanggalWaktu")
        .copy()
    )

    available_months = sorted(
        monthly_snapshots["Bulan"]
        .dropna()
        .unique()
        .tolist()
    )

    # --------------------------------------------------------
    # Informasi jumlah bulan
    # --------------------------------------------------------

    st.metric(
        "📅 Bulan Tersedia",
        len(available_months)
    )

    # --------------------------------------------------------
    # Grafik trend
    # --------------------------------------------------------

    if len(available_months) < 2:

        st.info(
            "Data belum cukup untuk menampilkan "
            "trend antar-bulan. "
            "Minimal diperlukan data dari 2 bulan berbeda."
        )

    else:

        trend_df = monthly_snapshots.copy()

        trend_df["Label"] = trend_df.apply(
            lambda row:
            row["Kode"]
            if pd.notna(row["Kode"])
            and str(row["Kode"]) != "-"
            else row["Nama"],
            axis=1
        )

        fig_monthly = px.line(
            trend_df,
            x="Bulan",
            y="Score",
            color="Label",
            markers=True,
            hover_data=[
                "Nama",
                "Sektor",
                "MaximumScore",
                "Status"
            ],
            title="Perkembangan Score Antar-Bulan"
        )

        fig_monthly.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Score",
            height=500
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )

    # --------------------------------------------------------
    # Perbandingan bulan terbaru
    # --------------------------------------------------------

    if len(available_months) < 2:

        st.subheader("📊 Perbandingan Bulanan")

        st.info(
            "Belum ada bulan sebelumnya untuk dibandingkan."
        )

    else:

        latest_month = available_months[-1]
        previous_month = available_months[-2]

        latest_month_df = monthly_snapshots[
            monthly_snapshots["Bulan"] == latest_month
        ].copy()

        previous_month_df = monthly_snapshots[
            monthly_snapshots["Bulan"] == previous_month
        ].copy()

        comparison_rows = []

        # ----------------------------------------------------
        # Bandingkan berdasarkan sektor
        # ----------------------------------------------------

        sectors = sorted(
            set(
                latest_month_df["Sektor"].dropna()
            ).intersection(
                set(
                    previous_month_df["Sektor"].dropna()
                )
            )
        )

        for sector in sectors:

            current_sector = latest_month_df[
                latest_month_df["Sektor"] == sector
            ]

            previous_sector = previous_month_df[
                previous_month_df["Sektor"] == sector
            ]

            if current_sector.empty:
                continue

            if previous_sector.empty:
                continue

            current_row = current_sector.iloc[0]
            previous_row = previous_sector.iloc[0]

            try:

                current_score = float(
                    current_row["Score"]
                )

                previous_score = float(
                    previous_row["Score"]
                )

            except (
                ValueError,
                TypeError
            ):

                continue

            change = (
                current_score
                - previous_score
            )

            if change > 0:
                trend = "NAIK"
            elif change < 0:
                trend = "TURUN"
            else:
                trend = "TETAP"

            comparison_rows.append({
                "Sektor": sector,
                "Kandidat Sebelumnya": (
                    previous_row["Kode"]
                    if str(previous_row["Kode"]) != "-"
                    else previous_row["Nama"]
                ),
                "Kandidat Sekarang": (
                    current_row["Kode"]
                    if str(current_row["Kode"]) != "-"
                    else current_row["Nama"]
                ),
                "Score Sebelumnya": previous_score,
                "Score Sekarang": current_score,
                "Perubahan": change,
                "Trend": trend
            })

        st.subheader(
            f"📊 {previous_month} → {latest_month}"
        )

        if comparison_rows:

            comparison_df = pd.DataFrame(
                comparison_rows
            )

            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Belum ditemukan data sektor yang dapat "
                "dibandingkan antar-bulan."
            )

    # --------------------------------------------------------
    # Data snapshot bulanan
    # --------------------------------------------------------

    st.subheader(
        "📋 Snapshot Bulanan"
    )

    monthly_display_columns = [
        "Bulan",
        "Sektor",
        "Kode",
        "Nama",
        "Score",
        "MaximumScore",
        "Status"
    ]

    available_monthly_columns = [
        col
        for col in monthly_display_columns
        if col in monthly_snapshots.columns
    ]

    st.dataframe(
        monthly_snapshots[
            available_monthly_columns
        ],
        use_container_width=True,
        hide_index=True
    )
# ============================================================
# DATA FRESHNESS & SOURCE
# ============================================================

st.divider()

st.header("📡 Data Quality")

st.write(
    "Informasi tanggal data dan sumber data yang digunakan "
    "pada hasil screening terbaru."
)

freshness_df = latest_df.copy()

if freshness_df.empty:

    st.info(
        "Tidak ada data screening terbaru."
    )

else:

    freshness_rows = []

    for _, row in freshness_df.iterrows():

        # ----------------------------------------------------
        # Kandidat
        # ----------------------------------------------------

        if (
            pd.notna(row.get("Kode"))
            and str(row.get("Kode")).strip() != "-"
        ):
            candidate = str(row["Kode"])
        else:
            candidate = str(row["Nama"])

        # ----------------------------------------------------
        # Tanggal data
        # ----------------------------------------------------

        raw_data_date = row.get("TanggalData")

        data_date = pd.to_datetime(
            raw_data_date,
            errors="coerce"
        )

        # ----------------------------------------------------
        # Sumber
        # ----------------------------------------------------

        source = row.get("Sumber", "-")

        if pd.isna(source) or str(source).strip() == "":
            source = "-"

        # ----------------------------------------------------
        # Hitung umur data
        # ----------------------------------------------------

        if pd.notna(data_date):

            screening_date = pd.Timestamp(
                latest_datetime
            ).normalize()

            data_date_only = data_date.normalize()

            age_days = (
                screening_date - data_date_only
            ).days

            if age_days < 0:
                freshness_status = "Tanggal data > screening"
            elif age_days <= 3:
                freshness_status = "Data terbaru"
            elif age_days <= 7:
                freshness_status = "Data relatif baru"
            else:
                freshness_status = "Perlu diperiksa"

            data_date_display = (
                data_date.strftime("%Y-%m-%d")
            )

        else:

            age_days = None
            freshness_status = "Tanggal data tidak tersedia"
            data_date_display = "-"

        freshness_rows.append({
            "Kandidat": candidate,
            "Sektor": row.get("Sektor", "-"),
            "Tanggal Data": data_date_display,
            "Sumber": source,
            "Umur Data (hari)": (
                age_days
                if age_days is not None
                else "-"
            ),
            "Status": freshness_status
        })

    freshness_table = pd.DataFrame(
        freshness_rows
    )

    st.dataframe(
        freshness_table,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Status umur data dihitung berdasarkan tanggal "
        "screening terbaru yang tersimpan di history."
    )
# ============================================================
# INFORMATION
# ============================================================

st.divider()

st.header("ℹ️ Informasi")

st.info(
    "Dashboard ini merupakan alat monitoring dan visualisasi "
    "hasil screening. Dashboard tidak memberikan perintah "
    "otomatis untuk membeli atau menjual saham."
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Stock Agent Dashboard V2 | "
    "Data: screening_history.csv"
)