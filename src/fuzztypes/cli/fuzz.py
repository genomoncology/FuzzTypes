import csv
from pathlib import Path

import click

from fuzztypes import FuzzValidator, const, find_matches, lazy, storage
from fuzztypes.cli import app


@app.command()
@click.argument("annotated_type", type=str)
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output_file", type=click.Path(), help="Output CSV file")
def fuzz(annotated_type: str, input_file: str, output_file: str):
    """Run fuzzing on a given annotated type."""
    library_name, attr_name = annotated_type.rsplit(".", maxsplit=1)
    annotated_type_obj = lazy.lazy_import(library_name, attr_name)
    fuzz_validator_obj = annotated_type_obj.__metadata__[0]
    assert isinstance(
        fuzz_validator_obj, FuzzValidator
    ), f"Invalid annotation: {annotated_type}"
    storage_obj = fuzz_validator_obj.func
    assert isinstance(
        storage_obj, storage.AbstractStorage
    ), f"Invalid annotation: {annotated_type}"

    input_path = Path(input_file)
    output_path = Path(
        output_file or input_path.with_name(f"{input_path.stem}-output.csv")
    )

    fieldnames = ["input"]
    scorers = list(const.FuzzScorer.__args__)  # type: ignore[attr-defined]
    for scorer in scorers:
        fieldnames.append(scorer)
        fieldnames.append(f"{scorer}_score")

    with open(input_path) as f, open(output_path, "w", newline="") as w:
        reader = filter(None, map(str.strip, f))
        writer = csv.DictWriter(w, fieldnames=fieldnames)
        writer.writeheader()

        for line in reader:
            output_row = {"input": line}

            for scorer in scorers:
                storage_obj.set_fuzz_scorer(scorer)
                matches = find_matches(storage_obj, line)

                best_value = "-"
                best_score = "0.0"
                if matches:
                    best_match = matches[0]
                    best_value = best_match.entity.value

                    if best_match.is_alias:
                        best_value += f" ({best_match.term})"
                    best_score = f"{best_match.score:.1f}"

                output_row[scorer] = best_value
                output_row[f"{scorer}_score"] = best_score

            writer.writerow(output_row)

    click.echo(f"Results saved to {output_file}")
