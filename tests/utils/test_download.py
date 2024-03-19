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
def mock_urlretrieve(mocker):
    return mocker.patch("urllib.request.urlretrieve")


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
    mock_path_exists, mock_file_age, mock_replace, mock_urlretrieve
):
    mock_path_exists.return_value = True
    mock_file_age.return_value = 31
    mock_urlretrieve.return_value = True

    result = get_file("http://example.com/file.txt")
    assert result == os.path.join(DownloadsPath, "file.txt")
    mock_replace.assert_called_once()
    mock_urlretrieve.assert_called_once_with(
        "http://example.com/file.txt",
        os.path.join(DownloadsPath, "file.txt.tmp"),
    )


def test_cache_miss_due_to_absence(
    mock_path_exists, mock_replace, mock_urlretrieve
):
    mock_path_exists.side_effect = [
        False,
        True,
    ]  # First call for cache check, second for download check
    mock_urlretrieve.return_value = True  # Simulate successful download
    assert get_file("http://example.com/file.txt") is not None
    mock_replace.assert_called_once()
    mock_urlretrieve.assert_called_once()


def test_download_failure(
    mock_path_exists, mock_logger_error, mock_urlretrieve
):
    mock_path_exists.return_value = False
    mock_urlretrieve.side_effect = Exception("Download failed")
    assert get_file("http://example.com/file.txt") is None
    mock_logger_error.assert_called_once()


def test_download_exception_handling(
    mock_path_exists, mock_logger_warning, mock_urlretrieve
):
    mock_path_exists.return_value = False
    mock_urlretrieve.side_effect = Exception(
        "Unexpected error"
    )  # Simulate an exception during download
    assert get_file("http://example.com/file.txt") is None
    mock_logger_warning.assert_called_once()
