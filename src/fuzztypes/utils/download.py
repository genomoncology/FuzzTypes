import os
import urllib.request
from datetime import datetime
from typing import Optional
from urllib.error import URLError, HTTPError

from fuzztypes import logger, const


def get_file_age_in_days(file_path: str) -> int:
    age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
    return age.days


def get_file(url: str, expires_in_days: int = 30) -> Optional[str]:
    """
    Tries to retrieve a file from the cache or download it if not available
    or expired.

    :param url: The URL of the original file to be downloaded.
    :param expires_in_days: Expiration period for the cached file.
    :return: Path to the downloaded file, or None if fails.
    """
    file_name = os.path.basename(url)
    cache_file_path = os.path.join(const.DownloadsPath, file_name)
    temp_download_path = f"{cache_file_path}.tmp"

    cache_ok = os.path.exists(cache_file_path)
    if cache_ok:
        file_age = get_file_age_in_days(cache_file_path)
        cache_ok = file_age <= expires_in_days

    if not cache_ok:
        download_success = download_file(url, temp_download_path)
        if download_success:
            os.replace(temp_download_path, cache_file_path)
            cache_ok = os.path.exists(cache_file_path)

    if not cache_ok:
        logger.error(f"Unable to download the file and no cached file: {url}")

    return cache_file_path if cache_ok else None


def download_file(url, download_path):
    """
    Attempt to download a file directly to a specified path.
    If the download fails, logs a warning and returns None.

    :param url: The URL of the file to be downloaded.
    :param download_path: The full file path where the file should be saved.
    :return: Boolean indicating success or failure of the download.
    """
    try:
        urllib.request.urlretrieve(url, download_path)
        return True
    except (HTTPError, URLError, ValueError, OSError, Exception) as e:
        logger.warning(f"Download (url={url}) failed: {e}", exc_info=True)
        return False
