import datetime
import requests
from pathlib import Path

def download_yuma_almanac(date, save_dir=".", raise_on_fail=False, overwrite=False, verbose=True):
    """
    Download a YUMA almanac for a given date from the USCG NAVCEN website.

    Parameters:
    -----------
    date : datetime.date
        Date for which the almanac should be downloaded.
    save_dir : str or Path
        Directory to save the downloaded file.
    raise_on_fail : bool
        If True, raise exception on failure instead of printing a message.
    overwrite : bool
        If True, overwrite the file if it already exists.
    verbose : bool
        If True, print status messages.

    Returns:
    --------
    str or None
        Path to the saved file if successful, else None.
    """
    try:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        year = date.year
        doy = date.timetuple().tm_yday
        url = f"https://navcen.uscg.gov/sites/default/files/gps/almanac/{year}/Yuma/{doy:03d}.alm"
        filename = save_dir / f"yumaAlmanac_{date.isoformat()}.alm"

        if filename.exists() and not overwrite:
            if verbose:
                print(f" File already exists: {filename}")
            return str(filename)

        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.content.strip():
            with open(filename, 'wb') as f:
                f.write(response.content)
            if verbose:
                print(f" Downloaded: {filename}")
            return str(filename)
        else:
            msg = f"Failed to download file (HTTP {response.status_code}) from: {url}"
            if raise_on_fail:
                raise RuntimeError(msg)
            if verbose:
                print(" " + msg)
            return None

    except requests.RequestException as e:
        msg = f"Request error: {e}"
    except OSError as e:
        msg = f"File I/O error: {e}"
    except Exception as e:
        msg = f"Unexpected error: {e}"

    if raise_on_fail:
        raise RuntimeError(msg)
    if verbose:
        print(" " + msg)
    return None
