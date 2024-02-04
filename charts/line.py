"""Streamlit ECharts Line chart defs"""

from typing import Iterable, Optional
from math import log, floor


_title_color: str = "#f2f4f3"
_background_color:str = "#1B2430"

def human_format(number) -> str:
    units = ["", " TYS", " MIL", " MLD", " TRL"]
    k = 1000.0
    prefix = "+"
    if number < 0:
        number *= -1
        prefix = "-"
    elif number == 0:
        return "0"
    magnitude = int(floor(log(number, k)))
    return f"{prefix}%.2f%s" % (number / k**magnitude, units[magnitude])


def get_totals_chart_opt(
    x: Iterable,
    series: list[dict],
    title: str,
    y_label: str,
    legend: Optional[list[str]] = None,
) -> dict:
    options = {
        "backgroundColor": _background_color,
        "title": {
            "text": title,
            "left": "center",
            "top": "top",
            "textStyle": {"color": _title_color},
        },
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "data": x,
            "axisLabel": {
                "textStyle": {
                    "color": _title_color,
                },
            },
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "splitLine": {
                "show": False,
            },
            "axisLabel": {
                "textStyle": {
                    "color": "#f77f00",
                },
            },
        },
        "series": series,
    }
    if legend:
        options["legned"] = {"data": legend}

    return options


def get_line_units_opt(
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
            "containLabel": True,
        },
        "backgroundColor": _background_color,
        "title": {
            "text": title,
            "left": "center",
            "top": "top",
            "textStyle": {"color": _title_color},
        },
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "data": x,
            "axisLabel": {
                "textStyle": {
                    "color": _title_color,
                },
            },
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "splitLine": {
                "show": False,
            },
            "axisLabel": {
                "textStyle": {
                    "color": _title_color,
                },
            },
        },
        "series": [
            {
                "name": serie["name"],
                "data": serie["data"],
                "type": "line",
                "smooth": True,
                "label": {
                    "show": False,
                    "position": "top",
                },
            }
            for serie in series
        ],
    }
    if legend:
        options["legend"] = {
            "data": legend,
            "bottom": 2,
            "textStyle": {"color": _title_color}

        }

    return options


def get_subunits_opt(
    x: Iterable,
    series: list[dict],
    title: str,
    y_label: str,
    legend: Optional[list[str]] = None,
) -> dict:
    options = {
        "grid": {
            "left": '2%',
            "right": '20%',
            "containLabel": True,
        },
        "backgroundColor": _background_color,
        "title": {
            "text": title,
            "left": "center",
            "top": "top",
            "textStyle": {"color": _title_color},
        },
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "data": x,
            "axisLabel": {
                "textStyle": {
                    "color": _title_color,
                },
            },
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "axisLabel": {
                "textStyle": {
                    "color": _title_color,
                },
            },
            "splitLine": {
                "show": False,
            },
        },
        "series": [
            {
                "name": serie["name"],
                "data": serie["data"],
                "type": "line",
                "smooth": True,
                "label": {
                    "show": True,
                    "position": "top",
                },
            }
            for serie in series
        ],
    }
    if legend:
        options["legend"] = {
                "data": legend,
                "right": 10,
                "top": "center",
                "orient": "vertical",
                "textStyle": {"color": _title_color}
            }

    return options

def get_totals_chart_expe_inco_opt(
    x: Iterable,
    series: list[dict],
    title: str,
    y_label: str,
    legend: Optional[list[str]] = None,
) -> dict:
    series_mod = []
    for elem in series:
        mark_points_data = []
        prev_val = None
        for idx, val in enumerate(elem["data"]):
            if prev_val:
                diff = float(val - prev_val)
                color = elem["up"] if diff > 0 else elem["down"]
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

        series_mod.append({
            "name": elem["name"],
            "data": elem["data"],
            "type": "line",
            "lineStyle": {"color": elem["color"]},
            "itemStyle": {"color": elem["color"]},
            "smooth": True,
            "label": {"show": True, "position": "top"},
            "markPoint": {"data": mark_points_data},
            })

    options = {
        "backgroundColor": _background_color,
        "title": {
            "text": title,
            "left": "center",
            "top": "top",
            "textStyle": {"color": _title_color},
        },
        "tooltip": {
            "trigger": "axis",
        },
        "xAxis": {
            "type": "category",
            "data": x,
            "axisLabel": {
                "textStyle": {
                    "color": _title_color,
                },
            },
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "splitLine": {
                "show": False,
            },
            "axisLabel": {
                "textStyle": {
                    "color": "#f77f00",
                },
            },
        },
        "series": series_mod,
    }
    if legend:
        options["legend"] = {
            "data": legend,
            "bottom": 0,
            "textStyle": {"color": _title_color}
        }

    return options
