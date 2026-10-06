# Copyright (c) 2026 Jonas Heinle

"""Unit tests for WebDavClient's path helpers and PROPFIND parsing; no server runs."""

from collections.abc import Callable
from pathlib import Path

import pytest

from kataglyphis_webdavclient import WebDavClient, webdavclient as module


PROPFIND_BODY = b"""<?xml version="1.0" encoding="utf-8"?>
<d:multistatus xmlns:d="DAV:">
  <d:response><d:href>/data/</d:href></d:response>
  <d:response><d:href>/data/a.txt</d:href></d:response>
  <d:response><d:href>/data/sub/</d:href></d:response>
  <d:response><d:href>/data/.hidden/</d:href></d:response>
  <d:response><d:href>/data/sub%20two/b.bin</d:href></d:response>
</d:multistatus>"""

# One recorded request: method, URL and headers.
Call = tuple[str, str, dict[str, str]]


class FakeResponse:
    """The two attributes the client reads from a requests.Response."""

    def __init__(self, status_code: int, content: bytes) -> None:
        """Hold the status and the body the client parses."""
        self.status_code = status_code
        self.content = content


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> WebDavClient:
    """Return a client; its constructor writes logs/ into a temporary directory."""
    monkeypatch.chdir(tmp_path)
    return WebDavClient("http://host:8080", "user", "secret")


@pytest.fixture
def stub_propfind(monkeypatch: pytest.MonkeyPatch) -> Callable[[int], list[Call]]:
    """Answer every request with PROPFIND_BODY and the given status; record calls."""

    def install(status: int) -> list[Call]:
        calls: list[Call] = []

        def fake_request(
            method: str, url: str, *, headers: dict[str, str], **_: object
        ) -> FakeResponse:
            calls.append((method, url, headers))
            return FakeResponse(status, PROPFIND_BODY)

        monkeypatch.setattr(module.requests, "request", fake_request)
        return calls

    return install


def test_filter_after_global_base_path_returns_what_follows_the_base(
    client: WebDavClient,
) -> None:
    """Everything after /<base>/ comes back; a path without it, unchanged."""
    assert (
        client.filter_after_global_base_path("/remote.php/data/x/y.txt", "data")
        == "x/y.txt"
    )
    assert (
        client.filter_after_global_base_path("/other/y.txt", "data") == "/other/y.txt"
    )


def test_get_sub_path_matches_a_whole_segment_and_decodes(client: WebDavClient) -> None:
    """The base must be a whole segment; an encoded remainder comes back decoded."""
    assert (
        client.get_sub_path("/data/subfolder1/text.txt", "data")
        == "subfolder1/text.txt"
    )
    assert client.get_sub_path("/data/sub%20folder/a.txt", "data") == "sub folder/a.txt"
    assert client.get_sub_path("/data/", "data") == ""
    with pytest.raises(ValueError, match="does not contain the initial part"):
        client.get_sub_path("/database/a.txt", "data")


def test_ensure_folder_exists_creates_nested_folders_once(
    client: WebDavClient, tmp_path: Path
) -> None:
    """Nested folders are created; a second call on an existing one is a no-op."""
    target = tmp_path / "a" / "b"
    client.ensure_folder_exists(str(target))
    client.ensure_folder_exists(str(target))
    assert target.is_dir()


def test_list_files_keeps_only_hrefs_without_a_trailing_slash(
    client: WebDavClient, stub_propfind: Callable[[int], list[Call]]
) -> None:
    """Folders end in a slash; every other href is a file, still percent-encoded."""
    calls = stub_propfind(207)
    files = client.list_files("http://host:8080/data")
    assert files == ["/data/a.txt", "/data/sub%20two/b.bin"]
    method, _, headers = calls[0]
    assert method == "PROPFIND"
    assert headers["Depth"] == "1"


def test_list_folders_drops_the_base_itself_and_hidden_folders(
    client: WebDavClient, stub_propfind: Callable[[int], list[Call]]
) -> None:
    """Only the visible child folders remain; the URL joins host and base path."""
    calls = stub_propfind(207)
    assert client.list_folders("data") == ["sub"]
    assert calls[0][1] == "http://host:8080/data"


@pytest.mark.parametrize("status", [401, 404, 500])
def test_listing_raises_unless_propfind_answers_207(
    client: WebDavClient,
    stub_propfind: Callable[[int], list[Call]],
    status: int,
) -> None:
    """A failed PROPFIND raises OSError naming the status, for files and folders."""
    stub_propfind(status)
    with pytest.raises(OSError, match=str(status)):
        client.list_files("http://host:8080/data")
    with pytest.raises(OSError, match=str(status)):
        client.list_folders("data")
