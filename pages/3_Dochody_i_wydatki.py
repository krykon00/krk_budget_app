"""Porównanie dochodów i wydatków budżetu"""

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from charts import line


st.set_page_config(
    page_icon="money_with_wings",
    page_title="Dochody i wydatki",
    initial_sidebar_state="expanded",
    layout="wide",
)



_f_path = Path(__file__).resolve().parents[1]  # app catalog path
data_path = f"{_f_path}/data/budget/doch_wyd"
years_list = []
df_doch = pd.DataFrame(columns=("Nazwa", "Ogółem", "Gmina", "Powiat"))
df_wyda = pd.DataFrame(columns=("Nazwa", "Ogółem", "Gmina", "Powiat"))
for file in sorted(os.listdir(data_path)):
    if file.endswith(".csv"):
        year = f"01.01.{file[8:12]}"
        years_list.append(year)
        next_df = pd.read_csv(f"{data_path}/{file}")
        if "Dochody" in file:
            df_doch = df_doch.merge(next_df, how="outer", on=["Nazwa"], suffixes=("", file[8:12]))
        else:
            df_wyda = df_wyda.merge(next_df, how="outer", on=["Nazwa"], suffixes=("", file[8:12]))
df_wyda.drop(columns=["Ogółem", "Gmina", "Powiat"], inplace=True)
df_wyda.fillna(0, inplace=True)
df_doch.drop(columns=["Ogółem", "Gmina", "Powiat"], inplace=True)
df_doch.fillna(0, inplace=True)

years_list = list(set(years_list))
names_list= sorted(list(set(list(df_doch["Nazwa"]) + list(df_wyda["Nazwa"]))))
with st.sidebar:
    st.image("https://www.bip.krakow.pl/zalaczniki/dokumenty/n/388864")
    st.markdown("### Filtry dla całego panelu:")
    years_filter = st.multiselect(
        label="Rok", placeholder="Wybierz lata", options=years_list
    )
    if years_filter:
        years_list = years_filter

    names_filter = st.multiselect(
        label="Nazwa",
        placeholder="Wybierz nazwę",
        options=names_list,
        )
    if names_filter:
        names_list = names_filter

for df in [df_doch, df_wyda]:
    for column in list(df.columns)[1:]:
        in_filters: bool = any(fyear[-4:] in column for fyear in years_list)
        if not in_filters:
            df.drop(columns=[column], inplace=True)

df_doch = df_doch[df_doch["Nazwa"].isin(names_list)]
df_wyda = df_wyda[df_wyda["Nazwa"].isin(names_list)]



totals_overall_expe = [float(df_wyda[f"Ogółem{year[-4:]}"].sum()) for year in years_list]
totals_overall_inco = [float(df_doch[f"Ogółem{year[-4:]}"].sum()) for year in years_list]
totals_gmina_expe = [float(df_wyda[f"Gmina{year[-4:]}"].sum()) for year in years_list]
totals_gmina_inco = [float(df_doch[f"Gmina{year[-4:]}"].sum()) for year in years_list]
totals_powiat_expe = [float(df_wyda[f"Powiat{year[-4:]}"].sum()) for year in years_list]
totals_powiat_inco = [float(df_doch[f"Powiat{year[-4:]}"].sum()) for year in years_list]

with st.container():
    st.header("Dochody i wydatki planowane w budżecie")
    st.divider()
    with st.container():
        st.markdown("#### Wykres planowanych przychodów i wydatków w budżecie")
        series = [
                {"name": "Dochody ogółem", "data": totals_overall_inco, "color": "#0a9396", "up": "#588157", "down": "#d90429"},
                {"name": "Wydatki ogółem", "data": totals_overall_expe, "color": "#d62828", "up": "#d90429", "down":"#588157"},
        ]
        st_echarts(
            options=line.get_totals_chart_expe_inco_opt(
                x=years_list,
                series=series,
                title="Histria planowanych dochodów i wydatków ogółem w budżecie",
                y_label="PLN",
                legend=["Dochody ogółem", "Wydatki ogółem"]
        ))
    with st.container():
        st.markdown("#### Wykres planowanych przychodów i wydatków w budżecie dla gminy i powiatu")
        totals_gmina_col, totals_powiat_col = st.columns(2)
        with totals_gmina_col:
            series = [
                {"name": "Dochody ogółem", "data": totals_gmina_inco, "color": "#0a9396", "up": "#588157", "down": "#d90429"},
                {"name": "Wydatki ogółem", "data": totals_gmina_expe, "color": "#d62828", "up": "#d90429", "down":"#588157"},
            ]
            st_echarts(
                options=line.get_totals_chart_expe_inco_opt(
                    x=years_list,
                    series=series,
                    title="Planowane dochody i przychody gminy",
                    y_label="PLN",
                    legend=["Dochody ogółem", "Wydatki ogółem"]
            ))
        with totals_powiat_col:
            series = [
                {"name": "Dochody ogółem", "data": totals_powiat_inco, "color": "#0a9396", "up": "#588157", "down": "#d90429"},
                {"name": "Wydatki ogółem", "data": totals_powiat_expe, "color": "#d62828", "up": "#d90429", "down":"#588157"},
            ]
            st_echarts(
                options=line.get_totals_chart_expe_inco_opt(
                    x=years_list,
                    series=series,
                    title="Planowane dochody i przychody powiatu",
                    y_label="PLN",
                    legend=["Dochody ogółem", "Wydatki ogółem"]
            ))
    with st.container():
        st.markdown("#### Pełna tabela danych")
        st.markdown("##### Planowane dochody")
        st.dataframe(df_doch, use_container_width=True)
        st.divider()
        st.markdown("##### Planowane wydatki")
        st.dataframe(df_wyda, use_container_width=True)
