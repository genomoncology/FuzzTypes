import csv
import json
from pathlib import Path
from typing import Generator, Type


def from_jsonl(
    path: Path, mv_splitter: str = "|"
) -> Generator[dict, None, None]:
    """
    Generates entity dictionaries from a .jsonl file, streaming each line as a
    JSON object. This method conserves memory for large files.

    :param path: Path to the .jsonl file.
    :param mv_splitter: Used to split multi-value fields.
    :return: Generator yielding entity dictionaries.
    """
    with path.open() as fp:
        for line in fp:
            yield json.loads(line)


def from_csv(
    path: Path, mv_splitter: str = "|"
) -> Generator[dict, None, None]:
    """
    Streams entity dictionaries from a .csv file, optimizing memory usage
    for large files.

    :param path: Path to the .csv file.
    :param mv_splitter: Splits multi-value fields.
    :return: Generator yielding entity dictionaries.
    """
    yield from from_sv(path, csv.excel, mv_splitter=mv_splitter)


def from_tsv(
    path: Path, mv_splitter: str = "|"
) -> Generator[dict, None, None]:
    """
    Streams entity dictionaries from a .tsv file, conserving memory for
    large files.

    :param path: Path to the .tsv file.
    :param mv_splitter: Splits multi-value fields.
    :return: Generator yielding entity dictionaries.
    """
    yield from from_sv(path, csv.excel_tab, mv_splitter=mv_splitter)


def from_txt(
    path: Path, mv_splitter: str = "|"
) -> Generator[dict, None, None]:
    """
    Streams entity dictionaries from a .txt file, assuming a single field
    per line. Efficient for large text files.

    :param path: Path to the .txt file.
    :param mv_splitter: Splits multi-value fields.
    :return: Generator yielding entity dictionaries.
    """
    yield from from_sv(
        path, csv.excel, fieldnames=["name"], mv_splitter=mv_splitter
    )


def from_sv(
    path: Path, dialect: Type[csv.Dialect], fieldnames=None, mv_splitter="|"
) -> Generator[dict, None, None]:
    """
    Generic function to stream entities from structured format files (CSV/TSV),
    specified by the dialect. Underpins from_csv, from_tsv, from_txt.

    :param path: Path to the file.
    :param dialect: CSV/TSV dialect for parsing.
    :param fieldnames: Optional fieldnames for header-less files.
    :param mv_splitter: Splits multi-value fields.
    :return: Generator yielding entity dictionaries.
    """

    with path.open() as fp:
        yield from csv.DictReader(fp, dialect=dialect, fieldnames=fieldnames)


def from_file(
    path: Path, mv_splitter: str = "|"
) -> Generator[dict, None, None]:
    """
    Determines the file type by extension and streams entities using the
    appropriate loader function. Provides a unified interface.

    :param path: Path to the file.
    :param mv_splitter: Splits multi-value fields.
    :return: Generator yielding entity dictionaries.
    """
    dialects = {
        ".csv": from_csv,
        ".tsv": from_tsv,
        ".jsonl": from_jsonl,
        ".txt": from_txt,
    }
    ext = path.suffix.lower()

    def fix(d: dict):
        aliases = d.get("aliases")
        if aliases and isinstance(aliases, str):
            d["aliases"] = list(filter(None, aliases.split(mv_splitter)))

        meta_keys = d.keys() - {"name", "aliases", "meta", "priority", "label"}
        if meta_keys:
            meta = d.setdefault("meta", {})
            for key in meta_keys:
                meta[key] = d.pop(key)

        return d

    if ext in dialects:
        reader = dialects[ext](path, mv_splitter=mv_splitter)
        yield from map(fix, reader)
    else:
        raise NotImplementedError(f"File type not supported: {ext}")
