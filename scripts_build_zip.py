from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
INCLUDE_PATHS = [
    "app.py",
    "README.md",
    "requirements.txt",
    "run_app.sh",
    "build_submission_zip.sh",
    "scripts_build_submission.py",
    "scripts_render_docx.py",
    "scripts_build_zip.py",
    ".streamlit",
    "agents",
    "tools",
    "schemas",
    "config",
    "knowledge",
    "data",
    "notebooks",
    "tests",
    "final_submission",
]


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    name = path.name
    if name in {".DS_Store"}:
        return True
    if parts & {"__pycache__", ".pytest_cache", ".venv", "outputs", ".ipynb_checkpoints"}:
        return True
    if path.as_posix() == "config/model_config.yaml":
        return True
    if path.parent.as_posix() == "data" and "副本" in name:
        return True
    if name.endswith(".zip"):
        return True
    return False


def _iter_files(root: Path):
    for include in INCLUDE_PATHS:
        path = root / include
        if not path.exists():
            continue
        if path.is_file():
            rel = path.relative_to(root)
            if not _should_skip(rel):
                yield path, rel
            continue
        for file_path in sorted(path.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(root)
            if not _should_skip(rel):
                yield file_path, rel


def build_zip(leader_name: str) -> Path:
    root_name = f"选题二_财报智析Agent_{leader_name}"
    zip_path = PROJECT_DIR / f"{root_name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path, rel in _iter_files(PROJECT_DIR):
            zf.write(file_path, f"{root_name}/{rel.as_posix()}")
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build UTF-8 submission zip for 财报智析 Agent.")
    parser.add_argument("leader_name", nargs="?", default="徐北辰", help="组长姓名")
    args = parser.parse_args()
    zip_path = build_zip(args.leader_name)
    print(f"已生成：{zip_path}")


if __name__ == "__main__":
    main()
