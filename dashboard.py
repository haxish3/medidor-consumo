import calendar
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from medidor_consumo.database import get_daily_totals

st.set_page_config(page_title="Medidor de Consumo", page_icon="⚡", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stMetricValue"] { font-size: 2rem; }
        [data-testid="stMetricLabel"] { color: #9ca3af; }
    </style>
    """,
    unsafe_allow_html=True,
)

root = Path(__file__).resolve().parent
db_path = root / "data" / "consum.db"


def load_today_samples(today: str) -> pd.DataFrame:
    query = """
        SELECT recorded_at, total_power_w, energy_kwh, cost_brl
        FROM samples
        WHERE recorded_at LIKE ?
        ORDER BY recorded_at
    """

    with sqlite3.connect(db_path, timeout=5) as connection:
        samples = pd.read_sql_query(query, connection, params=(f"{today}%",))

    if not samples.empty:
        samples["recorded_at"] = pd.to_datetime(samples["recorded_at"])

    return samples


@st.fragment(run_every=5)
def show_dashboard() -> None:
    now = datetime.now().astimezone()
    today = now.date()
    daily = pd.DataFrame(
        get_daily_totals(db_path), columns=["date", "energy_kwh", "cost_brl"]
    )

    if not daily.empty:
        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily[daily["date"].dt.date <= today]

    today_rows = daily[daily["date"].dt.date == today] if not daily.empty else daily
    today_kwh = float(today_rows["energy_kwh"].sum())
    today_cost_brl = float(today_rows["cost_brl"].sum())

    month_rows = (
        daily[
            (daily["date"].dt.year == now.year) & (daily["date"].dt.month == now.month)
        ]
        if not daily.empty
        else daily
    )
    month_kwh = float(month_rows["energy_kwh"].sum())
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    projected_kwh = month_kwh / now.day * days_in_month
    projected_cost_brl = projected_kwh * 0.82

    average_kwh = float(daily["energy_kwh"].mean()) if not daily.empty else 0.0
    average_cost_brl = float(daily["cost_brl"].mean()) if not daily.empty else 0.0

    st.title("⚡ Medidor de Consumo")
    st.caption(f"Dados de {today.strftime('%d/%m/%Y')} · atualiza a cada 5 segundos")

    today_column, cost_column, average_column, projection_column = st.columns(4)
    today_column.metric("Consumo hoje", f"{today_kwh:.3f} kWh")
    cost_column.metric("Custo hoje", f"R$ {today_cost_brl:.2f}")
    average_column.metric(
        "Média diária", f"{average_kwh:.3f} kWh", f"R$ {average_cost_brl:.2f}"
    )
    projection_column.metric(
        "Previsão do mês", f"{projected_kwh:.2f} kWh", f"R$ {projected_cost_brl:.2f}"
    )

    if daily.empty:
        st.info("Ainda não há dados salvos.")
        return

    biggest_day = daily.loc[daily["energy_kwh"].idxmax()]
    st.info(
        f"Maior consumo: {biggest_day['date'].strftime('%d/%m/%Y')} "
        f"com {biggest_day['energy_kwh']:.3f} kWh."
    )

    samples = load_today_samples(today.isoformat())
    power_column, energy_column = st.columns(2)

    with power_column:
        st.subheader("Potência ao longo do dia")
        if samples.empty:
            st.caption("O monitor ainda não gravou leituras de hoje.")
        else:
            power_chart = samples.set_index("recorded_at")[["total_power_w"]]
            st.line_chart(power_chart, height=280)

    with energy_column:
        st.subheader("Consumo acumulado hoje")
        if samples.empty:
            st.caption("O monitor ainda não gravou leituras de hoje.")
        else:
            samples["cumulative_kwh"] = samples["energy_kwh"].cumsum()
            energy_chart = samples.set_index("recorded_at")[["cumulative_kwh"]]
            st.line_chart(energy_chart, height=280)

    st.subheader("Histórico diário")
    daily_chart = daily.set_index("date")[["energy_kwh"]]
    st.bar_chart(daily_chart, height=250)


show_dashboard()
