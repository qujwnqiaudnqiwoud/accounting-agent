from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd


def load_financial_excel(file: str | Path | BinaryIO) -> pd.DataFrame:
    """Read the first non-empty worksheet from an uploaded financial Excel file."""
    try:
        sheets = pd.read_excel(file, sheet_name=None)
    except Exception as exc:  # pragma: no cover - exact engine errors vary
        raise ValueError(f"Excel 读取失败：{exc}") from exc

    for _, df in sheets.items():
        if not df.empty:
            df = df.dropna(how="all").dropna(axis=1, how="all")
            if not df.empty:
                return df
    raise ValueError("Excel 文件中没有可读取的数据表。")


def load_financial_table(file: str | Path | BinaryIO) -> pd.DataFrame:
    """Read a financial data file from Excel or CSV."""
    if isinstance(file, (str, Path)):
        path = Path(file)
        suffix = path.suffix.lower()
        if suffix == ".csv":
            last_error: Exception | None = None
            for encoding in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
                try:
                    return pd.read_csv(path, encoding=encoding)
                except UnicodeDecodeError as exc:
                    last_error = exc
                    continue
                except Exception as exc:  # pragma: no cover - exact parser errors vary
                    raise ValueError(f"CSV 读取失败：{exc}") from exc
            raise ValueError(f"CSV 编码识别失败：{last_error}")
        if suffix in {".xlsx", ".xls"}:
            return load_financial_excel(path)
        raise ValueError("仅支持读取 xlsx、xls、csv 格式的结构化财务数据。")
    return load_financial_excel(file)


def save_uploaded_file(uploaded_file, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(uploaded_file.getbuffer())
    return path
