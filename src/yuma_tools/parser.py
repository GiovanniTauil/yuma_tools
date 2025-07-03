import pandas as pd
import datetime
import re
from pathlib import Path

def parse_yuma_almanac(filepath, almanac_date=None, strict=True, verbose=True):
    """
    Parses a YUMA almanac file and returns a DataFrame with satellite records.

    Parameters:
    -----------
    filepath : str or Path
        Path to the YUMA almanac file.
    almanac_date : datetime.datetime, optional
        Date to assign to the 'Time' column. Defaults to file modification time (UTC).
    strict : bool
        If True, raise an error when mandatory fields are missing. If False, return best-effort parsing.
    verbose : bool
        If True, print diagnostic messages.

    Returns:
    --------
    pandas.DataFrame
        DataFrame with YUMA satellite parameters.
    """
    filepath = Path(filepath)
    if not filepath.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with filepath.open('r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        raise IOError(f"Failed to read file: {e}")

    if not lines:
        raise ValueError("Input file is empty")

    if almanac_date is None:
        almanac_date = datetime.datetime.fromtimestamp(
            filepath.stat().st_mtime,
            tz=datetime.timezone.utc
        )

    field_map = {
        "ID:": ("PRN", int),
        "Health:": ("Health", int),
        "Eccentricity:": ("Eccentricity", lambda x: float(x.replace("D", "E"))),
        "Time of Applicability(s):": ("TimeOfApplicability", lambda x: float(x.replace("D", "E"))),
        "Orbital Inclination(rad):": ("OrbitalInclination", lambda x: float(x.replace("D", "E"))),
        "Rate of Right Ascen(r/s):": ("RateOfRightAscen", lambda x: float(x.replace("D", "E"))),
        "SQRT(A)  (m 1/2):": ("SQRTA", lambda x: float(x.replace("D", "E"))),
        "Right Ascen at Week(rad):": ("RightAscenAtWeek", lambda x: float(x.replace("D", "E"))),
        "Argument of Perigee(rad):": ("ArgumentOfPerigee", lambda x: float(x.replace("D", "E"))),
        "Mean Anom(rad):": ("MeanAnom", lambda x: float(x.replace("D", "E"))),
        "Af0(s):": ("Af0", lambda x: float(x.replace("D", "E"))),
        "Af1(s/s):": ("Af1", lambda x: float(x.replace("D", "E")))
    }

    records = []
    record = {}
    week = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("******** Week"):
            match = re.search(r"Week\s+(\d+)", line)
            if match:
                week = int(match.group(1))

        elif line.startswith("ID:"):
            if record:
                records.append(record.copy())
            record = {'Week': week, 'Time': almanac_date}

            try:
                record['PRN'] = int(line.split(":", 1)[1].strip())
            except Exception:
                record['PRN'] = None
                if verbose:
                    print(f"Warning: Failed to parse PRN from line: {line}")

        else:
            for field, (key, converter) in field_map.items():
                if line.startswith(field) and field != "ID:":
                    try:
                        value = line.split(":", 1)[1].strip()
                        record[key] = converter(value)
                    except Exception:
                        record[key] = None
                        if verbose:
                            print(f"Warning: Failed to parse {key} from line: {line}")
                    break

    if record:
        records.append(record)

    if not records:
        raise ValueError("No valid records found in the YUMA file.")

    df = pd.DataFrame(records)

    required_fields = ['PRN', 'Week', 'Time']
    if strict:
        missing = [f for f in required_fields if f not in df.columns or df[f].isnull().all()]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

    df['Time'] = pd.to_datetime(df['Time'])

    if verbose:
        print(f" Parsed {len(df)} records from: {filepath}")

    return df
