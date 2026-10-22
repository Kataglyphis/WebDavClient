# Copyright (c) 2024 Jonas Heinle

"""WebDAV client implementation for listing and downloading remote files."""

import sys
import threading
import time
import urllib.parse
import uuid
from pathlib import Path, PurePosixPath

import requests
from defusedxml import ElementTree
from loguru import logger
from requests.auth import HTTPBasicAuth


REQUEST_TIMEOUT_SECONDS = 30
LOG_FILE = "logs/downloadMd_s.log"

# One loguru sink per log file: a sink per client wrote every line once per client and rotated the file N times.
_log_sinks: set[str] = set()
_log_sinks_lock = threading.Lock()


def _add_log_sink(log_file: str) -> None:
    path = str(Path(log_file).absolute())
    with _log_sinks_lock:
        if path in _log_sinks:
            return
        logger.add(path, rotation="500 MB")
        _log_sinks.add(path)


def _join_remote_url(*parts: str) -> str:
    cleaned_parts = [part.strip("/") for part in parts if part]
    return "/".join(cleaned_parts)


def _remote_relative_path(href: str, base_url: str) -> tuple[str, ...]:
    """Return validated, decoded path components below the same-origin DAV base."""
    if any(ord(char) < 32 for char in href):
        message = "WebDAV href contains control characters"
        raise ValueError(message)
    raw_path = urllib.parse.unquote(urllib.parse.urlsplit(href).path, errors="strict")
    if any(part in {".", ".."} for part in raw_path.split("/")):
        message = "WebDAV href contains an unsafe path component"
        raise ValueError(message)
    base = urllib.parse.urlsplit(base_url.rstrip("/") + "/")
    remote = urllib.parse.urlsplit(urllib.parse.urljoin(base.geturl(), href))
    if (remote.scheme, remote.netloc) != (base.scheme, base.netloc):
        message = "WebDAV href belongs to another origin"
        raise ValueError(message)
    if remote.query or remote.fragment:
        message = "WebDAV href contains a query or fragment"
        raise ValueError(message)
    path = urllib.parse.unquote(remote.path, errors="strict")
    base_path = urllib.parse.unquote(base.path, errors="strict").rstrip("/")
    parts = tuple(path.strip("/").split("/")) if path.strip("/") else ()
    base_parts = tuple(base_path.strip("/").split("/")) if base_path else ()
    # Validate before prefix matching so neither dot segments nor Windows syntax can change the destination.
    if any(
        not part
        or part in {".", ".."}
        or any(ord(char) < 32 or char in '\\:<>"|?*' for char in part)
        or part.endswith((".", " "))
        or part.split(".", 1)[0].rstrip(" ").upper()
        in {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in "123456789¹²³"),
            *(f"LPT{i}" for i in "123456789¹²³"),
        }
        for part in parts
    ):
        message = "WebDAV href contains an unsafe path component"
        raise ValueError(message)
    if parts[: len(base_parts)] != base_parts:
        message = "WebDAV href is outside the remote base path"
        raise ValueError(message)
    return parts[len(base_parts) :]


def _download_target(base: Path, relative: tuple[str, ...]) -> Path:
    """Resolve existing symlinks and reject a destination outside the download root."""
    target = base.joinpath(*relative).resolve()
    if not relative or not target.is_relative_to(base):
        message = "WebDAV download target is outside the local base path"
        raise ValueError(message)
    return target


def _replace(part: Path, target: Path) -> None:
    # Windows refuses a replace while another thread replaces the same target (PermissionError); it clears in milliseconds.
    attempts = 40 if sys.platform == "win32" else 1
    for attempt in range(attempts):
        try:
            part.replace(target)
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.005 * (attempt + 1))
        else:
            return


def _write_atomically(target: Path, response: requests.Response) -> None:
    # A private file renamed into place: two downloads of one file never interleave, and a reader never sees half of it.
    part = target.with_name(f".{target.name}.{uuid.uuid4().hex}.part")
    try:
        with part.open("xb") as f:
            f.writelines(response.iter_content(chunk_size=8192))
        _replace(part, target)
    except BaseException:
        part.unlink(missing_ok=True)
        raise


class WebDavClient:
    """A simple WebDav client for listing and downloading files and folders."""

    def __init__(self, hostname: str, username: str, password: str) -> None:
        """Initialize a client with credentials and logging output folder."""
        self.hostname: str = hostname
        self.username: str = username
        self.password: str = password
        self.auth: HTTPBasicAuth = HTTPBasicAuth(
            username,
            password,
        )

        self.ensure_folder_exists(str(Path(LOG_FILE).parent))
        _add_log_sink(LOG_FILE)

    def _hrefs(self, url: str) -> list[str]:
        headers: dict[str, str] = {"Content-Type": "application/xml", "Depth": "1"}
        with requests.request(
            "PROPFIND",
            url,
            auth=self.auth,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            if response.status_code != 207:
                message = f"Failed to list {url}: HTTP {response.status_code}"
                raise OSError(message)
            tree = ElementTree.fromstring(response.content)
        hrefs = []
        for item in tree.findall("{DAV:}response"):
            href = item.findtext("{DAV:}href")
            if not href:
                message = "WebDAV listing contains a response without an href"
                raise ValueError(message)
            hrefs.append(href)
        return hrefs

    def list_files(self, url: str) -> list[str]:
        """List the files directly below a WebDAV URL; OSError unless PROPFIND answers 207."""
        files = []
        for href in self._hrefs(url):
            if not href.endswith("/"):
                logger.debug("Found file: {} for the following url: {}", href, url)
                files.append(href)
        return files

    def list_folders(self, remote_base_path: str) -> list[str]:
        """List the non-hidden folders directly below a remote base path; OSError unless PROPFIND answers 207."""
        url: str = _join_remote_url(self.hostname, remote_base_path)
        folders = []
        for href in self._hrefs(url):
            if not href.endswith("/"):
                continue
            relative = _remote_relative_path(href, url)
            if not relative:
                continue
            if len(relative) != 1:
                message = "WebDAV folder is not a direct child of its parent"
                raise ValueError(message)
            if not relative[0].startswith("."):
                folders.append(urllib.parse.quote(relative[0], safe=""))
        return folders

    def filter_after_global_base_path(self, path: str, remote_base_path: str) -> str:
        """Return what follows /remote_base_path/ in path, or path unchanged when it is absent."""
        search_str = "/" + remote_base_path + "/"
        if search_str in path:
            logger.debug(
                "Found folder {} for path {} and remote base path: {}",
                search_str,
                path,
                remote_base_path,
            )
            url_after_removing_everything_before_and_including_remote_base_name = (
                path.split(search_str, 1)[1]
            )
            logger.info(
                "Folder structure everything after the remote_base_path is: {}",
                url_after_removing_everything_before_and_including_remote_base_name,
            )
            return url_after_removing_everything_before_and_including_remote_base_name
        logger.error("Could not find search string: {} in path: {}", search_str, path)
        return path

    def ensure_folder_exists(self, path: str) -> None:
        """Ensure that the given folder exists."""
        folder_path = Path(path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug("Folder created: {}", path)
        else:
            logger.debug("Folder already exists: {}", path)

    def get_sub_path(self, full_path: str, initial_part: str) -> str:
        """Return the part of a host-less full_path after initial_part; ValueError when it is absent."""
        logger.debug("We are in the 'get_sub_path' method.")
        decoded_full_path = urllib.parse.unquote(full_path)
        logger.debug("The decoded full file path is: {}", decoded_full_path)
        decoded_initial_part = urllib.parse.unquote(initial_part)
        logger.debug("The decoded initial file path is: {}", decoded_initial_part)
        # A trailing slash makes the match a whole path segment.
        if not decoded_initial_part.endswith("/"):
            decoded_initial_part += "/"

        start_idx = decoded_full_path.find(decoded_initial_part)

        if start_idx == -1:
            logger.error(
                "The {} string is not in the full_path={}", initial_part, full_path
            )
            error_details = "The full path does not contain the initial part."
            raise ValueError(error_details)

        # Handle the edge case where the full path is exactly the initial part
        decoded_initial_part = "/" + decoded_initial_part
        if full_path == decoded_initial_part.rstrip("/"):
            logger.debug("The get_sub_path() method returns empty string")
            return ""

        if full_path.startswith(initial_part):
            logger.debug(
                "The get_sub_path() method returns {}", full_path[len(initial_part) :]
            )
            return full_path[len(initial_part) :]
        sub_path_start_idx = start_idx + len(decoded_initial_part) - 1

        sub_path = decoded_full_path[sub_path_start_idx:]

        logger.debug("The get_sub_path() method returns {}", sub_path)

        return sub_path

    def download_files(
        self,
        global_remote_base_path: str,
        remote_base_path: str,
        local_base_path: str,
        *,
        extension: str | None = None,
    ) -> int:
        """Atomically download matching files, preserving paths below the global base; return the count."""
        base = Path(local_base_path).resolve()
        base.mkdir(parents=True, exist_ok=True)
        global_url = _join_remote_url(self.hostname, global_remote_base_path)
        url = _join_remote_url(self.hostname, remote_base_path)
        files_on_host = self.list_files(url)
        written = 0
        for file_path in files_on_host:
            relative = _remote_relative_path(file_path, global_url)
            local_file_path = _download_target(base, relative)
            if extension and not relative[-1].lower().endswith(extension.lower()):
                continue
            remote_file_url = urllib.parse.urljoin(url.rstrip("/") + "/", file_path)
            with requests.get(
                remote_file_url,
                auth=self.auth,
                stream=True,
                timeout=REQUEST_TIMEOUT_SECONDS,
            ) as response:
                if response.status_code != 200:
                    message = f"Failed to download {remote_file_url}: HTTP {response.status_code}"
                    raise OSError(message)
                local_file_path.parent.mkdir(parents=True, exist_ok=True)
                _write_atomically(_download_target(base, relative), response)
            written += 1
        return written

    def download_all_files_iterative(
        self,
        remote_base_path: str,
        local_base_path: str,
        *,
        extension: str | None = None,
    ) -> int:
        """Download a tree with an optional case-insensitive suffix; fail on any error and return the count."""
        stack: list[str] = [remote_base_path]
        written = 0
        global_remote_base_path: str = remote_base_path

        while stack:
            current_remote_path: str = stack.pop()
            logger.debug("Current remote path is: {}", current_remote_path)

            written += self.download_files(
                global_remote_base_path,
                current_remote_path,
                local_base_path,
                extension=extension,
            )

            folders: list[str] = self.list_folders(current_remote_path)
            if len(folders) == 0:
                logger.info(
                    "Found no subfolders for current folder: {}", current_remote_path
                )
            for folder in folders:
                # Folder listings return one encoded component, never a remote path to traverse.
                relative = _remote_relative_path(
                    folder,
                    _join_remote_url(self.hostname, current_remote_path),
                )
                if len(relative) != 1:
                    message = "WebDAV folder is not a direct child of its parent"
                    raise ValueError(message)
                logger.info(
                    "Found subfolder {} for current folder: {}.",
                    folder,
                    current_remote_path,
                )
                relative_folder_path: str = str(
                    PurePosixPath(current_remote_path) / folder
                )
                stack.append(relative_folder_path)
        return written
