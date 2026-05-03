import pandas as pd


def _column_match_score(series: pd.Series, keywords) -> int:
    return sum(
        series.str.contains(kw, case=False, na=False, regex=True).sum()
        for kw in keywords
    )


def find_column(
    df: pd.DataFrame,
    *,
    column_name_keywords=None,
    content_keywords=None,
    excluded_columns=None,
    exclude_url=False,
):
    excluded = set(excluded_columns or [])
    best_column, best_score = None, -1

    for col in df.columns:
        if col in excluded:
            continue
        if column_name_keywords and not any(
            kw.lower() in col.lower() for kw in column_name_keywords
        ):
            continue

        series = df[col].astype(str)
        if exclude_url and series.str.contains(r"https?://", na=False).any():
            continue

        if content_keywords:
            score = _column_match_score(series, content_keywords)
            if score == 0:
                continue
            if score > best_score:
                best_column, best_score = col, score
        else:
            return col

    if best_column is not None:
        return best_column

    raise ValueError(
        f"Could not auto-detect column for "
        f"name_keywords={column_name_keywords} content_keywords={content_keywords}"
    )
