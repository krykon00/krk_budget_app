"""Functions for manipulating data for ease of passing values into charts"""

import pandas as pd


def df_to_series(df: pd.DataFrame) -> list[dict]:
    """Transform rows of data into series and 1st df column into series names"""
    series = []
    label_col = df.columns[0]
    other_cols = df.columns[1:]
    for _, row in df.iterrows():
        series.append(
            {
                "name": str(row[label_col]),
                "data": [row[col] for col in other_cols],
            }
        )

    return series
