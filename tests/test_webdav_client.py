# Copyright (c) 2024 Jonas Heinle

"""Tests for the WebDavClient against a local mock WebDAV server."""

import shutil
import threading
import time
from collections.abc import Iterator
from multiprocessing import Process
from pathlib import Path
from uuid import uuid4

import pytest
from loguru import logger

from kataglyphis_webdavclient import WebDavClient
from tests.mock_webdav_server import create_web_dav_server


def cleanup_test_files() -> None:
    """Remove local test directories created during download tests."""
    for folder in ("tests/local_data", "tests/local_data2", "tests/local_data3"):
        try:
            shutil.rmtree(folder)
        except OSError as error:
            logger.error("Cleanup error: {}", error.strerror)
    logger.info("Removed local test directories.")


@pytest.fixture(scope="module", autouse=True)
def start_webdav_server() -> Iterator[None]:
    """Start the mock WebDAV server for all tests in this module."""
    server_process = Process(target=create_web_dav_server, daemon=True)
    server_process.start()

    time.sleep(4)
    yield

    server_process.terminate()
    server_process.join(timeout=10)
    cleanup_test_files()


@pytest.fixture
def webdav_client() -> WebDavClient:
    """Provide a configured WebDavClient for local integration tests."""
    hostname = "http://localhost:8081"
    username = "testuser"
    password = uuid4().hex
    return WebDavClient(hostname, username, password)


def test_filter_after_global_base_path(webdav_client: WebDavClient) -> None:
    """Filter paths relative to the global remote base path."""
    path = "/data/subfolder1/text.txt"
    path2 = "http://localhost:8081/data"
    remote_base_path = "data"
    result = webdav_client.filter_after_global_base_path(path, remote_base_path)
    result2 = webdav_client.filter_after_global_base_path(path2, remote_base_path)
    assert result == "subfolder1/text.txt"
    assert result2 == path2


def test_list_files(webdav_client: WebDavClient) -> None:
    """List files directly in the remote root folder."""
    remote_base_path = "data"
    url = f"{webdav_client.hostname.rstrip('/')}/{remote_base_path}"
    files = webdav_client.list_files(url)
    assert "/data/Readme.md" in files


def test_list_folders(webdav_client: WebDavClient) -> None:
    """List direct subfolders below the remote root folder."""
    folders = webdav_client.list_folders("data")
    assert "subfolder1" in folders
    assert "subfolder2" in folders
    assert "subfolder3" in folders


def test_get_sub_path(webdav_client: WebDavClient) -> None:
    """Compute a relative sub-path from a full path and base path."""
    full_path = "/data/subfolder1/text.txt"
    initial_part = "data"
    result = webdav_client.get_sub_path(full_path, initial_part)
    assert result == "subfolder1/text.txt"


def test_download_files(webdav_client: WebDavClient) -> None:
    """Download files from the current remote folder without recursion."""
    global_remote_base_path = "data"
    remote_base_path = "data"
    local_base_path = "tests/local_data"

    webdav_client.download_files(
        global_remote_base_path,
        remote_base_path,
        local_base_path,
    )
    assert (Path(local_base_path) / "Readme.md").exists()


def test_download_all_files_iterative(webdav_client: WebDavClient) -> None:
    """Download files recursively while preserving directory structure."""
    remote_base_path = "data"
    local_base_path = "tests/local_data2"

    webdav_client.download_all_files_iterative(remote_base_path, local_base_path)
    assert (Path(local_base_path) / "Readme.md").exists()
    assert (Path(local_base_path) / "subfolder1/text.txt").exists()


def test_concurrent_downloads_into_one_tree(webdav_client: WebDavClient) -> None:
    """Threads sharing one client and one destination each leave complete files and no partial ones."""
    local_base_path = Path("tests/local_data3")
    threads_count = 8
    barrier = threading.Barrier(threads_count)
    errors: list[BaseException] = []

    def download() -> None:
        barrier.wait()
        try:
            webdav_client.download_all_files_iterative("data", str(local_base_path))
        except BaseException as error:  # the main thread asserts on it
            errors.append(error)

    threads = [threading.Thread(target=download) for _ in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    remote = Path("tests/remote/data")
    expected = sorted(p.relative_to(remote) for p in remote.rglob("*") if p.is_file())
    got = sorted(
        p.relative_to(local_base_path)
        for p in local_base_path.rglob("*")
        if p.is_file()
    )
    assert got == expected
    for relative in expected:
        assert (local_base_path / relative).read_bytes() == (
            remote / relative
        ).read_bytes()


if __name__ == "__main__":
    _ = start_webdav_server
    pytest.main()
