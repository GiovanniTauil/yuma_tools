import pandas as pd
import datetime
import re
from pathlib import Path
from .parser import parse_yuma_almanac

def yumaread(
    filename,
    time_format="%Y-%m-%d",
    float_precision=None,
    display=False,
    strict=True,
    verbose=True
):
    """
    Reads a YUMA almanac file and returns a pandas DataFrame with parsed content.

    Parameters:
    -----------
    filename : str or Path
        Path to the YUMA almanac file.
    time_format : str or None
        Format string for the 'Time' column (e.g., '%Y-%m-%d'). If None, no formatting is applied.
    float_precision : int or None
        Decimal precision for float columns in display. None = full precision.
    display : bool
        Whether to print the DataFrame in formatted form.
    strict : bool
        If True, raise error when required fields are missing or malformed.
    verbose : bool
        If True, print status messages.

    Returns:
    --------
    pandas.DataFrame or None
        Parsed almanac as DataFrame (indexed by 'Time'), or None on error.
    """
    try:
        filename = Path(filename)

        if not filename.is_file():
            raise FileNotFoundError(f"File not found: {filename}")

        almanac_date = None
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", filename.name)
        if match:
            try:
                almanac_date = datetime.datetime(
                    int(match.group(1)), int(match.group(2)), int(match.group(3)),
                    tzinfo=datetime.timezone.utc
                )
            except Exception:
                if verbose:
                    print(f"Warning: Failed to parse date from filename: {filename.name}")

        if verbose:
            print(f"Parsing YUMA file: {filename}")

        df = parse_yuma_almanac(filename, almanac_date=almanac_date, strict=strict, verbose=verbose)

        if 'Time' not in df.columns:
            raise ValueError("Parsed data missing 'Time' column.")

        if time_format:
            try:
                df['Time'] = df['Time'].dt.strftime(time_format)
            except Exception as e:
                if verbose:
                    print(f"Warning: Could not format 'Time' column: {e}")

        df.set_index('Time', inplace=True)

        if display:
            float_cols = df.select_dtypes(include='float').columns
            if float_precision is not None:
                format_dict = {col: f"{{:.{float_precision}f}}" for col in float_cols}
            else:
                format_dict = {col: "{:.16f}" for col in float_cols}
            styled = df.style.format(format_dict)
            print(styled.to_string())

        return df

    except Exception as e:
        if verbose:
            print(f"Error processing file '{filename}': {e}")
        return None
