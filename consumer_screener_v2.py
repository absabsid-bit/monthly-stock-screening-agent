import yfinance as yf
import pandas as pd

# ============================================================
# CONSUMER SCREENER V2
# Tambahan:
# - Debt / Equity
# - Free Cash Flow
# ============================================================

STOCKS = {
    "ICBP.JK": "PT Indofood CBP Sukses Makmur Tbk",
    "INDF.JK": "PT Indofood Sukses Makmur Tbk",
    "MYOR.JK": "PT Mayora Indah Tbk",
    "UNVR.JK": "PT Unilever Indonesia Tbk",
    "SIDO.JK": "PT Industri Jamu dan Farmasi Sido Muncul Tbk",
}


# ============================================================
# FUNGSI SCORE
# ============================================================

def score_roe(roe):
    if roe >= 25:
        return 20
    elif roe >= 20:
        return 18
    elif roe >= 15:
        return 15
    elif roe >= 12:
        return 12
    elif roe >= 10:
        return 9
    elif roe >= 7:
        return 5
    else:
        return 0


def score_profit_growth(growth):
    if growth >= 20:
        return 15
    elif growth >= 15:
        return 13
    elif growth >= 10:
        return 11
    elif growth >= 5:
        return 9
    elif growth > 0:
        return 6
    elif growth >= -5:
        return 3
    else:
        return 0


def score_revenue_growth(growth):
    if growth >= 15:
        return 10
    elif growth >= 10:
        return 9
    elif growth >= 5:
        return 8
    elif growth > 0:
        return 6
    elif growth >= -5:
        return 3
    else:
        return 0


def score_equity_growth(growth):
    if growth >= 15:
        return 10
    elif growth >= 10:
        return 9
    elif growth >= 5:
        return 8
    elif growth > 0:
        return 6
    elif growth >= -5:
        return 3
    else:
        return 0


def score_consistency(consistency):
    if consistency == 3:
        return 15
    elif consistency == 2:
        return 10
    elif consistency == 1:
        return 5
    else:
        return 0


def score_per(per):
    if per <= 10:
        return 15
    elif per <= 15:
        return 13
    elif per <= 20:
        return 10
    elif per <= 25:
        return 7
    elif per <= 35:
        return 4
    else:
        return 0


def score_pbv(pbv):
    if pbv <= 1.5:
        return 15
    elif pbv <= 2:
        return 13
    elif pbv <= 3:
        return 10
    elif pbv <= 4:
        return 7
    elif pbv <= 6:
        return 4
    else:
        return 0


# ============================================================
# SCORE TAMBAHAN V2
# ============================================================

def score_debt_equity(de):
    if pd.isna(de):
        return 0
    elif de <= 0.25:
        return 5
    elif de <= 0.50:
        return 4
    elif de <= 0.75:
        return 3
    elif de <= 1.00:
        return 2
    elif de <= 1.50:
        return 1
    else:
        return 0


def score_fcf(fcf):
    if pd.isna(fcf):
        return 0
    elif fcf > 0:
        return 5
    else:
        return 0


# ============================================================
# AMBIL DATA
# ============================================================

results = []

for ticker, name in STOCKS.items():

    print(f"Memproses {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        info = stock.info
        income = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cashflow

        # ----------------------------------------------------
        # METRIK UTAMA
        # ----------------------------------------------------

        roe = info.get("returnOnEquity", float("nan"))
        per = info.get("trailingPE", float("nan"))
        pbv = info.get("priceToBook", float("nan"))

        if pd.notna(roe):
            roe = roe * 100

        # ----------------------------------------------------
        # NET INCOME
        # ----------------------------------------------------

        net_income = None

        if "Net Income" in income.index:
            net_income = income.loc["Net Income"].dropna()

        if net_income is not None and len(net_income) >= 2:
            profit_latest = net_income.iloc[0]
            profit_previous = net_income.iloc[1]

            if profit_previous != 0:
                profit_growth = (
                    (profit_latest - profit_previous)
                    / abs(profit_previous)
                ) * 100
            else:
                profit_growth = float("nan")
        else:
            profit_growth = float("nan")

        # ----------------------------------------------------
        # REVENUE
        # ----------------------------------------------------

        revenue = None

        if "Total Revenue" in income.index:
            revenue = income.loc["Total Revenue"].dropna()

        if revenue is not None and len(revenue) >= 2:
            revenue_latest = revenue.iloc[0]
            revenue_previous = revenue.iloc[1]

            if revenue_previous != 0:
                revenue_growth = (
                    (revenue_latest - revenue_previous)
                    / abs(revenue_previous)
                ) * 100
            else:
                revenue_growth = float("nan")
        else:
            revenue_growth = float("nan")

        # ----------------------------------------------------
        # EQUITY
        # ----------------------------------------------------

        equity = None

        if "Stockholders Equity" in balance.index:
            equity = balance.loc["Stockholders Equity"].dropna()

        if equity is not None and len(equity) >= 2:
            equity_latest = equity.iloc[0]
            equity_previous = equity.iloc[1]

            if equity_previous != 0:
                equity_growth = (
                    (equity_latest - equity_previous)
                    / abs(equity_previous)
                ) * 100
            else:
                equity_growth = float("nan")
        else:
            equity_growth = float("nan")

        # ----------------------------------------------------
        # KONSISTENSI LABA
        # 3 tahun terakhir
        # ----------------------------------------------------

        consistency = 0

        if net_income is not None and len(net_income) >= 4:

            profits = net_income.iloc[:4].tolist()

            for i in range(3):
                if profits[i] > profits[i + 1]:
                    consistency += 1

        # ----------------------------------------------------
        # DEBT / EQUITY
        # ----------------------------------------------------

        total_debt = float("nan")
        total_equity = float("nan")

        if "Total Debt" in balance.index:
            debt_series = balance.loc["Total Debt"].dropna()

            if len(debt_series) > 0:
                total_debt = debt_series.iloc[0]

        if "Stockholders Equity" in balance.index:
            equity_series = balance.loc["Stockholders Equity"].dropna()

            if len(equity_series) > 0:
                total_equity = equity_series.iloc[0]

        if (
            pd.notna(total_debt)
            and pd.notna(total_equity)
            and total_equity != 0
        ):
            debt_equity = total_debt / total_equity
        else:
            debt_equity = float("nan")

        # ----------------------------------------------------
        # FREE CASH FLOW
        # ----------------------------------------------------

        fcf = float("nan")

        if "Free Cash Flow" in cashflow.index:

            fcf_series = cashflow.loc["Free Cash Flow"].dropna()

            if len(fcf_series) > 0:
                fcf = fcf_series.iloc[0]

        else:

            operating_cf = float("nan")
            capex = float("nan")

            if "Operating Cash Flow" in cashflow.index:
                ocf_series = cashflow.loc[
                    "Operating Cash Flow"
                ].dropna()

                if len(ocf_series) > 0:
                    operating_cf = ocf_series.iloc[0]

            if "Capital Expenditure" in cashflow.index:
                capex_series = cashflow.loc[
                    "Capital Expenditure"
                ].dropna()

                if len(capex_series) > 0:
                    capex = capex_series.iloc[0]

            if pd.notna(operating_cf) and pd.notna(capex):
                fcf = operating_cf + capex

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        s_roe = score_roe(roe)
        s_profit = score_profit_growth(profit_growth)
        s_revenue = score_revenue_growth(revenue_growth)
        s_equity = score_equity_growth(equity_growth)
        s_consistency = score_consistency(consistency)
        s_per = score_per(per)
        s_pbv = score_pbv(pbv)
        s_de = score_debt_equity(debt_equity)
        s_fcf = score_fcf(fcf)

        total_score = (
            s_roe
            + s_profit
            + s_revenue
            + s_equity
            + s_consistency
            + s_per
            + s_pbv
            + s_de
            + s_fcf
        )

        # ----------------------------------------------------
        # FILTER MINIMUM
        # ----------------------------------------------------

        passed = (
            pd.notna(roe)
            and roe >= 10
            and pd.notna(profit_growth)
            and profit_growth > 0
            and pd.notna(revenue_growth)
            and revenue_growth > 0
            and consistency >= 2
        )

        if passed:
            status = "LULUS"
        else:
            status = "TIDAK LULUS"

        results.append({
            "Ticker": ticker,
            "Name": name,
            "Score": total_score,
            "Status": status,
            "ROE": roe,
            "ProfitGrowth": profit_growth,
            "RevenueGrowth": revenue_growth,
            "EquityGrowth": equity_growth,
            "Consistency": consistency,
            "PER": per,
            "PBV": pbv,
            "DebtEquity": debt_equity,
            "FCF": fcf,
        })

    except Exception as e:

        print(f"ERROR {ticker}: {e}")


# ============================================================
# HASIL
# ============================================================

df = pd.DataFrame(results)

if len(df) == 0:

    print("\nTidak ada data yang berhasil diproses.")

else:

    df_pass = df[df["Status"] == "LULUS"].copy()

    df_pass = df_pass.sort_values(
        by="Score",
        ascending=False
    )

    print("\n")
    print("=" * 70)
    print("              HASIL CONSUMER SCREENING V2")
    print("=" * 70)

    if len(df_pass) == 0:

        print("Tidak ada saham yang memenuhi filter.")

    else:

        for i, row in enumerate(df_pass.itertuples(), start=1):

            print(
                f"{i}. {row.Ticker:<10} "
                f"SCORE: {row.Score:>3}/110"
            )

    print("\n")

    if len(df_pass) > 0:

        candidate = df_pass.iloc[0]

        print("=" * 70)
        print("             KANDIDAT CONSUMER V2 #1")
        print("=" * 70)

        print(f"Kode       : {candidate['Ticker']}")
        print(f"Nama       : {candidate['Name']}")
        print(f"Score      : {candidate['Score']}/110")
        print(f"Status     : {candidate['Status']}")

        print("\nDATA UTAMA")
        print("-" * 50)

        print(
            f"ROE                : "
            f"{candidate['ROE']:.2f}%"
        )

        print(
            f"Growth laba        : "
            f"{candidate['ProfitGrowth']:+.2f}%"
        )

        print(
            f"Growth revenue     : "
            f"{candidate['RevenueGrowth']:+.2f}%"
        )

        print(
            f"Growth equity      : "
            f"{candidate['EquityGrowth']:+.2f}%"
        )

        print(
            f"Konsistensi laba   : "
            f"{int(candidate['Consistency'])}/3"
        )

        print(
            f"PER                : "
            f"{candidate['PER']:.2f}x"
        )

        print(
            f"PBV                : "
            f"{candidate['PBV']:.2f}x"
        )

        print(
            f"Debt/Equity        : "
            f"{candidate['DebtEquity']:.2f}x"
        )

        print(
            f"Free Cash Flow     : "
            f"{candidate['FCF']:,.0f}"
        )

    print("\n")
    print("=" * 70)
    print("          CONSUMER SCREENER V2 SELESAI")
    print("=" * 70)