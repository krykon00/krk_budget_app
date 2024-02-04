"""Dane z tabeli porównawczej kwot przeznaczonych dla dzielnic"""

import os
from pathlib import Path
from math import log, floor

import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from charts import line, bar
from charts.model import df_to_series

def human_format(number) -> str:
    units = ["", " TYS", " MIL", " MLD", " TRL"]
    k = 1000.0
    prefix = "+"
    if number < 0:
        number *= -1
        prefix = "-"
    magnitude = int(floor(log(number, k)))
    return f"{prefix}%.2f%s" % (number / k**magnitude, units[magnitude])


st.set_page_config(
    page_icon="money_with_wings",
    page_title="Wydatki dla dzielnic",
    initial_sidebar_state="expanded",
    layout="wide",
)


_f_path = Path(__file__).resolve().parents[1]  # app catalog path
data_path = f"{_f_path}/data/budget/districts"
years_list = []
df = pd.DataFrame(columns=["Rodzaj", "Wyszczególnienie"])
for file in sorted(os.listdir(data_path)):
    if file.endswith(".csv"):
        year = file[21:31].replace("_", ".")
        years_list.append(year)
        next_df = pd.read_csv(f"{data_path}/{file}")
        next_df.drop(columns=["Dział ", "Rozdział"], inplace=True)
        df = df.merge(next_df, how="outer", on=["Rodzaj", "Wyszczególnienie"])
df.fillna(0, inplace=True)
df["Rodzaj"] = df["Rodzaj"].apply(lambda x: x.strip())

types_list = list(df["Rodzaj"].unique())
details_list = list(df["Wyszczególnienie"].unique())

with st.sidebar:
    st.image("https://www.bip.krakow.pl/zalaczniki/dokumenty/n/388864")
    st.markdown("### Filtry dla całego panelu:")
    years_filter = st.multiselect(
        label="Rok", placeholder="Wybierz lata", options=years_list
    )
    if years_filter:
        years_list = years_filter
    types_filter = st.multiselect(
        label="Rodzaj",
        placeholder="Wybierz rodzaje",
        options=list(df["Rodzaj"].unique()),
    )
    if types_filter:
        types_list = types_filter
    details_filter = st.multiselect(
        label="Szczegół",
        placeholder="Wybierz szczegóły",
        options=list(df[df["Rodzaj"].isin(types_list)]["Wyszczególnienie"].unique()),
    )
    if details_filter:
        details_list = details_filter

for column in list(df.columns)[2:]:
    in_filters: bool = any(fyear in column for fyear in years_list)
    if not in_filters:
        df.drop(columns=[column], inplace=True)

df = df[df["Wyszczególnienie"].isin(details_list)]


totals = {
    year: df[f"Plan wydatków na {year} r."].sum() for year in years_list}


with st.container():
    st.header("Budżet Krakowa przeznaczony dla dzielnic:")
    st.divider()
    with st.container():
        st.markdown("#### Wykres sumy wdatków na dzielnice")
        data = []
        mark_points_data = []
        prev_val = None
        for idx, val in enumerate(totals.values()):
            data.append(val)
            if prev_val:
                diff = float(val - prev_val)
                color = "#a53860" if diff > 0 else "#014f86"
                symbol_rotate = 0 if diff > 0 else -180
                mark_points_data.append(
                    {
                        "name": f"P{idx}",
                        "value": human_format(diff),
                        "xAxis": idx,
                        "yAxis": val,
                        "symbol": "triangle",
                        "itemStyle": {"color": color},
                        "symbolRotate": symbol_rotate,
                        "symbolSize": 20,
                        "symbolOffset": [0, "150%"],
                    }
                )
            prev_val = val
        totals_series = [
            {
                "name": "Suma",
                "data": data,
                "type": "line",
                "lineStyle": {"color": "#f77f00"},
                "itemStyle": {"color": "#f77f00"},
                "smooth": True,
                "label": {"show": True, "position": "top"},
                "markPoint": {"data": mark_points_data},
            }
        ]
        st_echarts(
            options=line.get_totals_chart_opt(
                title="Suma kwoty budżetu na dzielnice",
                x=years_list,
                series=totals_series,
                y_label="PLN",
            )
        )
    with st.container():
        st.markdown("#### Wykres sumy wydatków na rodzaj")
        df_sum_type = df.drop(columns="Wyszczególnienie")
        df_sum_type = df_sum_type[df_sum_type["Rodzaj"].isin(types_list)].groupby(by=["Rodzaj"], as_index=False).agg("sum")
        series = df_to_series(df_sum_type)
        st_echarts(
            height="500px",
            options=line.get_subunits_opt(
                x=years_list,
                series=series,
                title="Suma budżetu dla dzielnic na rodzaje",
                y_label="PLN",
                legend=list(df_sum_type["Rodzaj"]),
                ))
    with st.container():
        st.markdown("#### Wykres spłupkowy budżetu dla dzielnic na rodzaj")
        types_bar_chart_col, types_bar_chart_ctrl_col = st.columns([5, 1])
        with types_bar_chart_ctrl_col:
            st.markdown("#### Filtry wykresu słupkowego:")
            tbcc_radio_sort = st.radio(
                label="Sortowanie",
                options=["Rosnoąco", "Malejąco"],
                index=0,
            )
            top_n_bar_units = st.slider(
                label="Top n wartości", min_value=0, max_value=15, value=None, step=1
            )
        with types_bar_chart_col:
            newest_value: str = f"Plan wydatków na {years_list[-1]} r."
            sub_df_sort = False if tbcc_radio_sort == "Malejąco" else True
            df_sum_type = df_sum_type[["Rodzaj", newest_value]].sort_values(
                by=newest_value, ascending=sub_df_sort
            )
            df_sum_type = df_sum_type[df_sum_type[newest_value] > 0]
            if top_n_bar_units:
                df_sum_type = df_sum_type.head(top_n_bar_units)
            st_echarts(
                options=bar.get_bar_by_types_opt(
                    title=f"Budżet dzielnic w rozbicu na rodzaj na {years_list[-1]}",
                    x=list(df_sum_type["Rodzaj"]),
                    y_label="PLN",
                    series=[{"data": list(df_sum_type[newest_value]), "name": "Rodzaj"}],
                )
            )
    with st.container():
        st.markdown("#### Wykres historyczny budżetu dla dzielnic w rozbicu na szczegóły rodzaju")
        chart_detail_col, detail_filters_col = st.columns([5, 1])
        with detail_filters_col:
            st.markdown("#### Filtr wykresu ")
            rodzaj = st.selectbox(
                label="Jednostka budżetowa",
                options=list(df["Rodzaj"].unique()),
                index=0,
                placeholder="Wybierz rodzaj",
            )
        with chart_detail_col:
            df_detail = df[df["Rodzaj"] == rodzaj]
            df_detail.drop(columns=["Rodzaj"], inplace=True)
            series = df_to_series(df_detail)
            st_echarts(
                height="500px",
                options=line.get_subunits_opt(
                    x=years_list,
                    series=series,
                    title=f"Szegóły budżetu dla: {rodzaj}",
                    y_label="PLN",
                    legend=list(df_detail["Wyszczególnienie"]),
                    ))

            


