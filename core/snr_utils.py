"""
SNR value hygiene helpers.

WSPR reports integer SNR values, but WSPRadar can introduce decimal values through
normalization, benchmark corrections, medians and bootstrap summaries. Keep those
values to one decimal place so exports and cached evidence do not imply false
binary-float precision such as -14.399999618530273.
"""

import pandas as pd


SNR_VALUE_COLUMNS = {
    "snr",
    "stat_val",
    "snr_u_norm",
    "snr_r_norm",
    "spot_diff",
    "bin_delta",
    "target_snr",
    "ref_snr",
    "t_med",
    "r_med",
    "micro_med_a",
    "micro_med_b",
}

SNR_NAME_MARKERS = (
    "snr",
    "norm@1w",
    "norm. snr",
    "micro-med",
    "bin \u0394",
    "\u0394 snr",
    "delta snr",
    "cycle ref median",
    "ref snr",
)


def is_snr_like_column_name(column_name):
    """Return True for displayed/exported columns that contain SNR-like values."""
    text = str(column_name).strip().lower()
    return any(marker in text for marker in SNR_NAME_MARKERS)


def round_snr_like_columns(df, columns=None, decimals=1):
    """Round known SNR-like dataframe columns while leaving other numeric data alone."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df

    rounded_df = df.copy()
    explicit_columns = columns is not None
    candidate_columns = columns if explicit_columns else rounded_df.columns
    for col in candidate_columns:
        if col in rounded_df.columns and (explicit_columns or col in SNR_VALUE_COLUMNS):
            rounded_df[col] = pd.to_numeric(rounded_df[col], errors="coerce").round(decimals)
    return rounded_df


def format_snr_like_columns_for_csv(df, decimals=1):
    """Return a CSV-facing copy with SNR-like values formatted to fixed precision."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df

    export_df = df.copy()
    for col in export_df.columns:
        if not is_snr_like_column_name(col):
            continue

        values = pd.to_numeric(export_df[col], errors="coerce")
        mask = values.notna()
        if not mask.any():
            continue

        export_df[col] = export_df[col].astype(object)
        export_df.loc[mask, col] = values.loc[mask].round(decimals).map(lambda value: f"{value:.{decimals}f}")
    return export_df
