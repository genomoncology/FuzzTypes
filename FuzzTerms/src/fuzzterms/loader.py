import csv
import json
from pathlib import Path
from typing import List, Type

from pydantic import TypeAdapter

from fuzzterms import Entity

EntityListAdapter = TypeAdapter(List[Entity])


def from_jsonl(path: Path, mv_splitter: str = "|") -> List[Entity]:
    """
    Constructs a list of Entities from a .jsonl file.

    :param path: Path object pointing to the .jsonl file.
    :param mv_splitter: String used to split multi-value fields.
    :return: List of Entities.
    """
    data = []
    with path.open() as fp:
        for line in fp:
            row = json.loads(line)

            aliases = row.pop("aliases", [])
            if aliases and isinstance(aliases, str):
                aliases = aliases.split(mv_splitter)
            row["aliases"] = aliases

            data.append(json.loads(line))

    return EntityListAdapter.validate_python(data)


def from_csv(path: Path, mv_splitter: str = "|") -> List[Entity]:
    return from_sv(path, csv.excel, mv_splitter=mv_splitter)


def from_tsv(path: Path, mv_splitter: str = "|") -> List[Entity]:
    return from_sv(path, csv.excel_tab, mv_splitter=mv_splitter)


def from_txt(path: Path, mv_splitter: str = "|") -> List[Entity]:
    return from_sv(
        path,
        csv.excel,
        fieldnames=["name"],
        mv_splitter=mv_splitter,
    )


def from_sv(
    path: Path,
    dialect: Type[csv.Dialect],
    fieldnames=None,
    mv_splitter="|",
) -> List[Entity]:
    """
    Constructs an EntityList from a .csv or .tsv file.

    :param path: Path object pointing to the .csv or .tsv file.
    :param dialect: CSV or TSV excel-based dialect.
    :param fieldnames: Specify header if not provided (e.g. .txt mode)
    :param mv_splitter: Multi-value splitter (e.g. '|')
    :return: List of Entities
    """

    def fix(d):
        aliases = d.get("aliases", "").split(mv_splitter)
        d["aliases"] = list(filter(None, aliases))
        return d

    with path.open() as fp:
        reader = csv.DictReader(fp, dialect=dialect, fieldnames=fieldnames)
        data = map(fix, list(reader))

    return EntityListAdapter.validate_python(data)


def from_file(path: Path, mv_splitter: str = "|") -> List[Entity]:
    """
    Constructs an EntityList from a file.

    :param path: Path object pointing to the file.
    :param mv_splitter: Multi-value splitter (e.g. '|')
    :return: List of Entities
    """
    dialects = {
        ".csv": from_csv,
        ".tsv": from_tsv,
        ".jsonl": from_jsonl,
        ".txt": from_txt,
    }
    ext = path.suffix.lower()

    if ext in dialects:
        return dialects[ext](path, mv_splitter=mv_splitter)
    else:
        raise NotImplementedError(f"File type not supported: {ext}")
