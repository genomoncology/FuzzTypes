import os.path

import pytest

from fuzztypes.const import DownloadsPath
from fuzztypes.utils.download import get_file


@pytest.fixture
def mock_path_exists(mocker):
    return mocker.patch("os.path.exists")


@pytest.fixture
def mock_getmtime(mocker):
    return mocker.patch("os.path.getmtime")


@pytest.fixture
def mock_replace(mocker):
    return mocker.patch("os.replace")


@pytest.fixture
def mock_file_age(mocker):
    return mocker.patch("fuzztypes.utils.download.get_file_age_in_days")


@pytest.fixture
def mock_urlopen(mocker):
    return mocker.patch("urllib.request.urlopen")


@pytest.fixture
def mock_logger_warning(mocker):
    return mocker.patch("fuzztypes.logger.warning")


@pytest.fixture
def mock_logger_error(mocker):
    return mocker.patch("fuzztypes.logger.error")


def test_get_file_cache_hit(mock_path_exists, mock_file_age, mock_replace):
    mock_path_exists.return_value = True
    mock_file_age.return_value = 10

    result = get_file("http://example.com/file.txt")
    assert result == os.path.join(DownloadsPath, "file.txt")
    mock_replace.assert_not_called()


def test_cache_miss_due_to_expiry(
    mock_path_exists, mock_file_age, mock_replace, mock_urlopen
):
    mock_path_exists.return_value = True
    mock_file_age.return_value = 31
    mock_urlopen.return_value.__enter__.return_value.read.return_value = (
        b"file content"
    )

    result = get_file("http://example.com/file.txt")
    assert result == os.path.join(DownloadsPath, "file.txt")
    mock_replace.assert_called_once()
    mock_urlopen.assert_called_once_with(
        "http://example.com/file.txt", timeout=120
    )


def test_save_to_new_file_name(
    mock_path_exists, mock_file_age, mock_replace, mock_urlopen
):
    mock_path_exists.return_value = True
    mock_file_age.return_value = 31
    mock_urlopen.return_value.__enter__.return_value.read.return_value = (
        b"file content"
    )

    result = get_file("http://example.com/file.txt", file_name="output.txt")
    assert result == os.path.join(DownloadsPath, "output.txt")
    mock_replace.assert_called_once()
    mock_urlopen.assert_called_once_with(
        "http://example.com/file.txt", timeout=120
    )


def test_cache_miss_due_to_absence(
    mock_path_exists, mock_replace, mock_urlopen
):
    mock_path_exists.side_effect = [
        True,  # Call for checking the downloads directory existence
        False,  # Call for cache check
        True,  # Call for download check
        True,  # Call for cache check after successful download
    ]
    mock_urlopen.return_value.__enter__.return_value.read.return_value = (
        b"file content"
    )

    assert get_file("http://example.com/file.txt") is not None
    mock_replace.assert_called_once()
    mock_urlopen.assert_called_once()


def test_download_failure(mock_path_exists, mock_logger_error, mock_urlopen):
    mock_path_exists.return_value = False
    mock_urlopen.side_effect = Exception("Download failed")

    assert get_file("http://example.com/file.txt") is None
    mock_logger_error.assert_called_once()


def test_download_exception_handling(
    mock_path_exists, mock_logger_warning, mock_urlopen
):
    mock_path_exists.return_value = False
    mock_urlopen.side_effect = Exception(
        "Unexpected error"
    )  # Simulate an exception during download

    assert get_file("http://example.com/file.txt") is None
    mock_logger_warning.assert_called_once()
