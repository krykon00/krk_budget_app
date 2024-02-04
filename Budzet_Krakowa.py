"""Main streamlit app file"""
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from charts import line

st.set_page_config(
    page_icon="money_with_wings",
    page_title="Wydatki bieżące",
    initial_sidebar_state="expanded",
    layout="wide",
)

_f_path = Path(__file__).resolve().parents[1]  # app catalog path
data_path = f"{_f_path}/app/data/budget"
df_dochody = pd.read_excel(f"{data_path}/data.xlsx", sheet_name="Dochody")
df_przychody= pd.read_excel(f"{data_path}/data.xlsx", sheet_name="Przychody")
df_wydatki = pd.read_excel(f"{data_path}/data.xlsx", sheet_name="Wydatki")
df_rozchody = pd.read_excel(f"{data_path}/data.xlsx", sheet_name="Rozchody")
dfs_list = [df_dochody, df_przychody, df_wydatki, df_rozchody]
years_list = sorted(list(df_dochody.columns)[1:])



with st.sidebar:
    st.image("https://www.bip.krakow.pl/zalaczniki/dokumenty/n/388864")
    st.markdown("### Filtry dla całego panelu:")
    years_filter = st.multiselect(
        label="Rok", placeholder="Wybierz lata", options=years_list
    )
    if years_filter:
        years_list = years_filter
print(years_list)

for df in dfs_list:
    df.fillna(0, inplace=True)
    for column in list(df.columns)[1:]:
        if not column in years_list:
            df.drop(columns=[column], inplace=True)

data_dochody = [float(df_dochody[year].loc[0]) for year in years_list]
data_sum_przychody = [float(df_przychody[year].sum()) for year in years_list]
przychody_ogolem = [sum(values) for values in zip(data_dochody, data_sum_przychody)]
data_wydatki = [float(df_wydatki[year].loc[0]) for year in years_list]
data_sum_rozchody = [float(df_rozchody[year].sum()) for year in years_list]
rozchody_ogolem = [sum(values) for values in zip(data_wydatki, data_sum_rozchody)]

with st.container():
    st.header("Budżet miasta Krakowa.")
    st.markdown("# Przychody i rozchody:")
    st.divider()
    with st.container():
        series =[
            {"name": "Dochody i przychody", "data": przychody_ogolem, "color": "#0a9396", "up": "#588157", "down": "#d90429"},
            {"name": "Wydatki i rozchody", "data": rozchody_ogolem, "color": "#d62828", "up": "#d90429", "down": "#588157",},
        ]
        st_echarts(
            options=line.get_totals_chart_expe_inco_opt(
                x=years_list,
                series=series,
                title="Zestawienie wszystkich przychodów i rozchodów",
                y_label="PLN",
                legend=["Dochody i przychody", "Wydatki i rozchody"]
            ))
    with st.container():
        deficyt_col, rozchody_col = st.columns(2)
        with deficyt_col:
            series = [{
                "name": "Deficyt", 
                "data": [float(df_dochody[year].loc[1]) for year in years_list],
                "color": "#d62828", 
                "up": "#d90429", 
                "down": "#588157",
            }]
            st_echarts(
                options=line.get_totals_chart_expe_inco_opt(
                    x=years_list,
                    title="Historia deficytu budżetowego",
                    series = series,
                    y_label="PLN",
                ))
        with rozchody_col:
            nazwy_rochodów = list(df_rozchody["Nazwa"])
            series = []
            for idx, name in enumerate(nazwy_rochodów):
                series.append(
                    {
                        "name": name, 
                        "data": [float(df_rozchody[year].loc[idx]) for year in years_list],
                        "color": "#d62828", 
                        "up": "#d90429", 
                        "down": "#588157",},
                )
            st_echarts(
                options=line.get_totals_chart_expe_inco_opt(
                    x=years_list,
                    title="Historia rozchodów budżetowych",
                    series=series,
                    y_label="PLN",
                    legend=list(df_rozchody["Nazwa"]),
            ))
    with st.container():
        wydatki_col, przychody_col = st.columns(2)
        with wydatki_col:
            st_echarts(
                options=line.get_totals_chart_expe_inco_opt(
                    x=years_list,
                    title="Historia wydatków budżetowych",
                    series=[{
                        "name": "Wydatki", 
                        "data": data_wydatki,
                        "color": "#d62828", 
                        "up": "#d90429", 
                        "down": "#588157",
                    }],
                    y_label="PLN",
                    legend=nazwy_rochodów,
            ))
        with przychody_col:
            nazwy_przychodow = list(df_przychody["Nazwa"])
            series = []
            for idx, name in enumerate(nazwy_przychodow):
                series.append(
                    {
                        "name": name, 
                        "data": [float(df_przychody[year].loc[idx]) for year in years_list],
                        "color": "#0a9396", 
                        "up": "#588157", 
                        "down": "#d90429"
                    })
            st_echarts(
                options=line.get_totals_chart_expe_inco_opt(
                    x=years_list,
                    title="Historia przychodów budżetowych",
                    series=series,
                    y_label="PLN",
                    legend=nazwy_przychodow,
            ))
    st.divider()
    with st.container():
        st.markdown("#### Tabele danych")
        with st.container():
            df_dochody_col, df_przychody_col = st.columns(2)
            with df_dochody_col:
                st.markdown("##### Dochody")
                st.dataframe(df_dochody, use_container_width=True)
            with df_przychody_col:
                st.markdown("##### Przychody")
                st.dataframe(df_przychody, use_container_width=True)
        with st.container():
            df_wydatki_col, df_rozchody_col = st.columns(2)
            with df_wydatki_col:
                st.markdown("##### Wydatki")
                st.dataframe(df_wydatki, use_container_width=True)
            with df_rozchody_col:
                st.markdown("##### Rozchody")
                st.dataframe(df_rozchody, use_container_width=True)




