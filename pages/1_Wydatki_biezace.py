"""App sub page with current expanses dash"""

import os
from pathlib import Path
from math import log, floor

import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from charts import bar, line
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
    page_title="Wydatki bieżące",
    initial_sidebar_state="expanded",
    layout="wide",
)

_f_path = Path(__file__).resolve().parents[1]  # app catalog path
data_path = f"{_f_path}/data/budget/wydatki_biezace"
dfs: dict[str, pd.DataFrame] = {}
for file in sorted(os.listdir(data_path)):
    if file.endswith(".csv"):
        df = pd.read_csv(f"{data_path}/{file}")
        df = df[~df["Nazwa zadania"].isna()]
        for char in ["'", '"', "\n"]:
            df.replace(char, "", inplace=True)
        dfs[file[11:21]] = df

units_filter_list = sorted(list(dfs[list(dfs.keys())[0]]["Jednostka"].unique()))
with st.sidebar:
    st.image("https://www.bip.krakow.pl/zalaczniki/dokumenty/n/388864")
    st.markdown("### Filtry dla całego panelu:")
    year_filter = st.multiselect(
        label="Lata", placeholder="Wybierz lata", options=list(dfs.keys())
    )
    unit_filter = st.multiselect(
        label="Jednostka", placeholder="Wybierz jednostkę", options=units_filter_list
    )


if year_filter:
    for key in list(dfs.keys()):
        if key not in year_filter:
            del dfs[key]
if unit_filter:
    units_filter_list = unit_filter
    for key, item in dfs.items():
        dfs[key] = dfs[key][dfs[key]["Jednostka"].isin(unit_filter)]

totals = {key: item["Wydatki na zadania ogółem"].sum() for key, item in dfs.items()}
unit_totals = {}
for key, item in dfs.items():
    unit_totals[key] = (
        item[["Jednostka", "Wydatki na zadania ogółem"]]
        .groupby(by="Jednostka", as_index=False)
        .agg("sum")
    )

df_unit_totals = pd.DataFrame(columns=["Jednostka", "Wydatki na zadania ogółem"])
for key, item in dfs.items():
    next_df = (
        item[["Jednostka", "Wydatki na zadania ogółem"]]
        .groupby(by="Jednostka", as_index=False)
        .agg("sum")
    )
    df_unit_totals = df_unit_totals.merge(
        next_df, on="Jednostka", how="outer", suffixes=["", f"_{key}"]
    )
df_unit_totals.drop(columns=["Wydatki na zadania ogółem"], inplace=True)
df_unit_totals.fillna(0, inplace=True)

with st.container():
    st.header("Planowany budżet na wydatki bieżące Krakowa:")
    st.divider()
    with st.container():
        st.markdown(
            "#### Wykres sumy wdatków biezących na wszystkie jednostki budżetowe"
        )
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
                title="Suma wydatków na zadania bieżące ogółem",
                x=list(dfs.keys()),
                series=totals_series,
                y_label="PLN",
            )
        )
    with st.container():
        st.markdown("### Wykres liniowy wydatków na jednostki budżetowe")
        st_echarts(
            height="500px",
            options=line.get_line_units_opt(
                title="Wydatki na bieżące zadania na jednostkę",
                x=list(dfs.keys()),
                y_label="PLN",
                series=df_to_series(df_unit_totals),
                legend=list(df_unit_totals["Jednostka"]),
            ),
        )
    with st.container():
        st.markdown(
            "#### Wykres słupkowy wydatków na jednostkę budżetową najaktualniejszego budżetu:"
        )
        unit_bar_chart_col, unit_bar_chart_ctrl_col = st.columns([5, 1])
        with unit_bar_chart_ctrl_col:
            st.markdown("#### Filtry wykresu słupkowego:")
            ubcc_radio_sort = st.radio(
                label="Sortowanie",
                options=["Rosnoąco", "Malejąco"],
                index=0,
            )
            top_n_bar_units = st.slider(
                label="Top n wartości", min_value=0, max_value=15, value=None, step=1
            )

        with unit_bar_chart_col:
            newest_values: str = df_unit_totals.columns[-1]
            sub_df_sort = False if ubcc_radio_sort == "Malejąco" else True
            sub_df = df_unit_totals[["Jednostka", newest_values]].sort_values(
                by=newest_values, ascending=sub_df_sort
            )
            sub_df = sub_df[sub_df[newest_values] > 0]
            if top_n_bar_units:
                sub_df = sub_df.head(top_n_bar_units)
            show_bar_fn = bar.get_bar_by_types_opt if top_n_bar_units else bar.get_bar_by_units_opt
            st_echarts(
                options=show_bar_fn(
                    title=newest_values,
                    x=list(sub_df["Jednostka"]),
                    y_label="PLN",
                    series=[{"data": list(sub_df[newest_values]), "name": "Jednostka"}],
                )
            )
    with st.container():
        st.markdown(
            "#### Wykres historyczny wydatków na zadania wybranej jednosteki budżetowej"
        )
        chart_subunits_col, subunits_filters_col = st.columns([5, 1])
        with subunits_filters_col:
            st.markdown("#### Filtr wykresu zadań")
            subunit_selection = st.selectbox(
                label="Jednostka budżetowa",
                options=units_filter_list,
                index=0,
                placeholder="Wybierz jednostkę",
            )
        df_subunits = pd.DataFrame(
            columns=("Nazwa zadania", "Wydatki na zadania ogółem")
        )
        for key, item in dfs.items():
            next_df = item[item["Jednostka"] == subunit_selection]
            df_subunits = df_subunits.merge(
                next_df[["Nazwa zadania", "Wydatki na zadania ogółem"]],
                on="Nazwa zadania",
                how="outer",
                suffixes=["", f"_{key}"],
            )
        df_subunits.drop(columns=["Wydatki na zadania ogółem"], inplace=True)
        df_subunits.fillna(0, inplace=True)
        with chart_subunits_col:
            st_echarts(
                height="500px",
                options=line.get_subunits_opt(
                    title=f"Zadania jed.: {subunit_selection}",
                    x=list(dfs.keys()),
                    y_label="PLN",
                    series=df_to_series(df_subunits),
                    legend=list(df_subunits["Nazwa zadania"]),
                ),
            )

