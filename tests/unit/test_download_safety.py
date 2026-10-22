# Copyright (c) 2026 Jonas Heinle

"""Exercise actual download paths and interrupted transfers without a remote server."""

from collections.abc import Iterator
from pathlib import Path
from types import TracebackType

import pytest

from kataglyphis_webdavclient import WebDavClient, webdavclient as module


class DownloadResponse:
    """A streaming response whose chunks can fail after an initial write."""

    def __init__(self, chunks: tuple[bytes | OSError, ...], status: int = 200) -> None:
        """Hold the body, HTTP status and response lifetime."""
        self.chunks = chunks
        self.status_code = status
        self.closed = False

    def __enter__(self) -> "DownloadResponse":  # noqa: PYI034 -- Keep the test double importable on Python 3.10.
        """Return the open response."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Record closure on success and errors."""
        self.closed = True

    def iter_content(self, chunk_size: int) -> Iterator[bytes]:
        """Yield body chunks or the simulated network failure."""
        assert chunk_size > 0
        for chunk in self.chunks:
            if isinstance(chunk, OSError):
                raise chunk
            yield chunk


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> WebDavClient:
    """Keep constructor logs inside the test directory."""
    monkeypatch.chdir(tmp_path)
    return WebDavClient("https://host.test", "user", "secret")


@pytest.mark.parametrize(
    "href",
    [
        "/data/%2e%2e/escaped.txt",
        "/data/../data/file.txt",
        "/data/dir/../../file.txt",
        "/data/C%3a%5cescaped.txt",
        "/data/%5c%5chost%5cshare%5ca.txt",
        "/data/%2fescape.txt",
        "/data/file.txt%3astream",
        "/data/NUL.txt",
        "/data/COM1",
        "/data/a%00.txt",
        "/data/a%1f.txt",
        "/data/NUL%20.txt",
        "/data/dir.%20/a.txt",
        "/database/file.txt",
        "https://another.test/data/file.txt",
        "/data/file.txt?query=1",
        "/data/file.txt#fragment",
    ],
)
def test_remote_href_cannot_escape_or_use_windows_path_syntax(
    client: WebDavClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    href: str,
) -> None:
    """Reject unsafe server names before making a GET request or writing a file."""
    monkeypatch.setattr(client, "list_files", lambda _: [href])

    def unexpected_get(*_args: object, **_kwargs: object) -> None:
        pytest.fail("unsafe href reached requests.get")

    monkeypatch.setattr(module.requests, "get", unexpected_get)
    root = tmp_path / "downloads"
    with pytest.raises(ValueError, match="WebDAV"):
        client.download_files("data", "data", str(root))
    assert list(root.iterdir()) == []


def test_filtered_tree_keeps_encoded_names_and_nested_relative_paths(
    client: WebDavClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A filtered transfer uses the same atomic writer as an unfiltered download."""
    client.hostname = "https://host.test/webdav"
    files = {
        "https://host.test/webdav/data": ["/webdav/data/skip.bin"],
        "https://host.test/webdav/data/sub%20folder": [
            "https://host.test/webdav/data/sub%20folder/a%20b.MD"
        ],
    }
    monkeypatch.setattr(client, "list_files", lambda url: files[url])
    monkeypatch.setattr(
        client, "list_folders", lambda path: ["sub%20folder"] if path == "data" else []
    )
    response = DownloadResponse((b"first", b"second"))
    urls: list[str] = []

    def get(url: str, **_kwargs: object) -> DownloadResponse:
        urls.append(url)
        return response

    monkeypatch.setattr(module.requests, "get", get)
    root = tmp_path / "downloads"
    assert client.download_all_files_iterative("data", str(root), extension=".md") == 1
    assert (root / "sub folder" / "a b.MD").read_bytes() == b"firstsecond"
    assert urls == ["https://host.test/webdav/data/sub%20folder/a%20b.MD"]
    assert response.closed
    assert not list(root.rglob("*.part"))


@pytest.mark.parametrize("status", [401, 404, 503])
def test_failed_get_raises_and_preserves_an_existing_target(
    client: WebDavClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: int,
) -> None:
    """HTTP failures must reach callers rather than reporting a successful tree."""
    monkeypatch.setattr(client, "list_files", lambda _: ["/data/a.txt"])
    response = DownloadResponse((b"error page",), status)
    monkeypatch.setattr(module.requests, "get", lambda *_args, **_kwargs: response)
    target = tmp_path / "a.txt"
    target.write_bytes(b"old")
    with pytest.raises(OSError, match=f"HTTP {status}"):
        client.download_files("data", "data", str(tmp_path))
    assert target.read_bytes() == b"old"
    assert response.closed


def test_interrupted_filtered_download_preserves_old_file_and_removes_part(
    client: WebDavClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failure after a body chunk cannot truncate the previous destination."""
    monkeypatch.setattr(client, "list_files", lambda _: ["/data/a.md"])
    response = DownloadResponse((b"incomplete", OSError("connection lost")))
    monkeypatch.setattr(module.requests, "get", lambda *_args, **_kwargs: response)
    target = tmp_path / "a.md"
    target.write_bytes(b"old")
    with pytest.raises(OSError, match="connection lost"):
        client.download_files("data", "data", str(tmp_path), extension=".md")
    assert target.read_bytes() == b"old"
    assert not list(tmp_path.rglob("*.part"))
    assert response.closed


def test_existing_symlink_cannot_redirect_a_download_outside_its_root(
    client: WebDavClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resolve existing directory links before opening the download's partial file."""
    root, outside = tmp_path / "downloads", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"host cannot create directory symlinks: {error}")
    monkeypatch.setattr(client, "list_files", lambda _: ["/data/link/a.txt"])
    with pytest.raises(ValueError, match="outside the local base"):
        client.download_files("data", "data", str(root))
    assert list(outside.iterdir()) == []


def test_listing_failure_reaches_the_recursive_caller(
    client: WebDavClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Filtering does not turn a failed listing into an empty successful result."""

    def list_files(_url: str) -> list[str]:
        message = "HTTP 503"
        raise OSError(message)

    monkeypatch.setattr(client, "list_files", list_files)
    with pytest.raises(OSError, match="HTTP 503"):
        client.download_all_files_iterative("data", str(tmp_path), extension=".md")


def test_propfind_closes_its_response_on_success_and_failure(
    client: WebDavClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Listing contexts close even if HTTP status or XML validation fails."""
    for status, content, expected_error in [
        (
            207,
            b'<multistatus xmlns="DAV:"><response><href>/data/a.txt</href></response></multistatus>',
            None,
        ),
        (503, b"unavailable", OSError),
        (207, b'<multistatus xmlns="DAV:"><response/></multistatus>', ValueError),
    ]:
        response = DownloadResponse((), status)
        response.content = content
        monkeypatch.setattr(
            module.requests,
            "request",
            lambda *_args, _response=response, **_kwargs: _response,
        )
        if expected_error:
            with pytest.raises(expected_error):
                client.list_files("https://host.test/data")
        else:
            assert client.list_files("https://host.test/data") == ["/data/a.txt"]
        assert response.closed


def test_folder_listing_retains_a_same_named_child_and_checks_the_remote_root(
    client: WebDavClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The self entry is a path comparison, and matching basenames do not hide real children."""
    monkeypatch.setattr(
        client, "_hrefs", lambda _: ["/data/", "/data/data/", "/data/sub%20dir/"]
    )
    assert client.list_folders("data") == ["data", "sub%20dir"]
    monkeypatch.setattr(client, "_hrefs", lambda _: ["/outside/child/"])
    with pytest.raises(ValueError, match="outside the remote base"):
        client.list_folders("data")
    monkeypatch.setattr(client, "_hrefs", lambda _: ["/", "/data/"])
    assert client.list_folders("") == ["data"]
