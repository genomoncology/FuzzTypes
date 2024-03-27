import csv
import tempfile
from typing import Annotated
from pathlib import Path

from click.testing import CliRunner

from fuzztypes import InMemoryValidator, flags
from fuzztypes.cli.fuzz import fuzz


def generate_combinations():
    words = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
    combinations = []
    for i in words:
        for j in words:
            for k in words:
                combinations.append(f"{i}{j}{k}")
    return combinations


all_combinations = set(generate_combinations())

# Create an annotated type for testing
TestCombination = Annotated[
    str,
    InMemoryValidator(
        all_combinations,
        search_flag=flags.FuzzSearch,
    ),
]


def test_fuzz_command():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_file = temp_path / "input.txt"
        output_file = temp_path / "input-output.csv"

        # Create the input file with test data
        test_inputs = [
            "Apple Banana Cherry",
            "Banana Cherry Date",
            "Cherry Date Elderberry",
            "Date Elderberry Apple",
            "Elderberry Apple Banana",
            "Apple Cherry Elderberry",
            "Banana Date Apple",
            "Cherry Elderberry Banana",
            "Date Apple Cherry",
            "Elderberry Banana Date",
            "Xylophone Yacht Zebra",
        ]
        with open(input_file, "w") as f:
            f.write("\n".join(test_inputs))

        # Run the fuzz command
        result = runner.invoke(
            fuzz,
            [
                "test_cli_fuzz.TestCombination",
                str(input_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Check the output CSV file
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == len(test_inputs)

            for row in rows:
                input_value = row["input"]
                assert input_value in test_inputs

                if input_value in all_combinations:
                    assert row["token_sort_ratio"] == input_value
                    assert row["token_sort_ratio_score"] == "100.0"
                else:
                    assert row["token_sort_ratio"] != input_value
                    assert float(row["token_sort_ratio_score"]) < 100.0
