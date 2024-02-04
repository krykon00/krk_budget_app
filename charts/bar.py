"""Streamlit ECharts Bar chart defs"""

from typing import Iterable, Optional

_title_color: str = "#f2f4f3"
_background_color:str = "#1B2430"


def get_bar_by_units_opt(
    x: Iterable,
    series: list[dict],
    title: str,
    y_label: str,
    legend: Optional[list[str]] = None,
) -> dict:
    options = {
        "grid": {
            "bottom": '25%',
            "left": "2%",
            "right": "2%",
            "containLabel": False,
        },
        "backgroundColor": _background_color,
        "title": {
            "text": title,
            "left": "center",
            "top": "top",
            "textStyle": {
                "color": _title_color,
            },
        },
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "data": x,
            "axisLabel": {
                "show": True,
                "rotate": 45,
                "color": _title_color,
            },
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "splitLine": {"show": False},
            "axisLabel": {
                "textStyle": {
                    "color": "#2ec4b6",
                },
            },
        },
        "series": [
            {
                "data": serie["data"],
                "name": serie["name"],
                "type": "bar",
                "itemStyle": {"color": "#2ec4b6"},
            }
            for serie in series
        ],
    }
    if legend:
        options["legned"] = {"data": legend}

    return options

def get_bar_by_types_opt(
    x: Iterable,
    series: list[dict],
    title: str,
    y_label: str,
    legend: Optional[list[str]] = None,
) -> dict:
    options = {
        "grid": {
            "bottom": '25%',
            "left": "2%",
            "right": "2%",
            "containLabel": False,
        },
        "backgroundColor": _background_color,
        "title": {
            "text": title,
            "left": "center",
            "top": "top",
            "textStyle": {
                "color": _title_color,
            },
        },
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "data": x,
            "axisLabel": {
                "show": True,
                "rotate": 45,
                "fontSize": 8,
                "color": _title_color,
            },
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "splitLine": {"show": False},
            "axisLabel": {
                "textStyle": {
                    "color": "#2ec4b6",
                },
            },
        },
        "series": [
            {
                "data": serie["data"],
                "name": serie["name"],
                "type": "bar",
                "itemStyle": {"color": "#2ec4b6"},
                "label": {
                    "show": True,
                    "position": "top",
                },
            }
            for serie in series
        ],
    }
    if legend:
        options["legned"] = {"data": legend}

    return options
