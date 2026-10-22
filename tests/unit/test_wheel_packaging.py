# Copyright (c) 2026 Jonas Heinle

"""Run the actual wheel rewriter without invoking setup or compiling extensions."""

import ast
import base64
import csv
import hashlib
import io
import runpy
import zipfile
from pathlib import Path


def test_stripped_binary_wheel_compresses_modules_and_keeps_a_valid_record(
    tmp_path: Path,
) -> None:
    """The shipped extension stays compressed, signed files go, and every retained byte is hashed."""
    setup_path = Path(__file__).resolve().parents[2] / "setup.py"
    tree = ast.parse(setup_path.read_text(encoding="utf-8"))
    node = next(
        item
        for item in tree.body
        if isinstance(item, ast.ClassDef) and item.name == "StripWheel"
    )
    namespace = {
        "_bdist_wheel": None,
        "rewrite_wheel": runpy.run_path(
            str(setup_path.parent / "build_support/kataglyphis_wheel.py")
        )["rewrite_wheel"],
        "Path": Path,
        "zipfile": zipfile,
        "hashlib": hashlib,
        "base64": base64,
    }
    exec(  # noqa: S102 -- Exercise the shipping class without setup() side effects.
        compile(ast.Module(body=[node], type_ignores=[]), str(setup_path), "exec"),
        namespace,
    )
    wheel = tmp_path / "client.whl"
    module_bytes = b"extension-code" * 8000
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("client/module.pyd", module_bytes)
        archive.writestr("client/module.py", "source")
        archive.writestr("client-1.dist-info/METADATA", "Name: client\n")
        archive.writestr("client-1.dist-info/RECORD", "stale")
        archive.writestr("client-1.dist-info/RECORD.jws", "stale signature")
    stripper = namespace["StripWheel"]()
    stripper._strip_wheel(wheel)  # noqa: SLF001 -- This is the rewriting entry point the build command calls.
    with zipfile.ZipFile(wheel) as archive:
        info = archive.getinfo("client/module.pyd")
        assert info.compress_type == zipfile.ZIP_DEFLATED
        assert info.compress_size < len(module_bytes) // 10
        assert "client/module.py" not in archive.namelist()
        assert "client-1.dist-info/RECORD.jws" not in archive.namelist()
        record = archive.read("client-1.dist-info/RECORD").decode()
        rows = list(csv.reader(io.StringIO(record)))
        assert rows[-1] == ["client-1.dist-info/RECORD", "", ""]
        for name, digest, size in rows[:-1]:
            data = archive.read(name)
            expected = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(
                b"="
            )
            assert digest == f"sha256={expected.decode()}"
            assert int(size) == len(data)
