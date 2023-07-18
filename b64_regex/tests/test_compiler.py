import pathlib
import re

from b64_regex.recoder import Segment


def get_data_path(filename: str) -> pathlib.Path:
    return pathlib.Path(__file__).parent / "data" / filename


def test_compiler_finds_matches():
    with open(get_data_path("test.txt"), "r") as f:
        lines = f.readlines()
    start_seq = Segment(b"HTB{")
    end_seq = Segment(b"}")

    pattern = re.compile(
        "(" f"{start_seq.as_regex()}" "[a-zA-Z0-9\\/\\+]+" f"{end_seq.as_regex()}" ")"
    )
    for entry in lines:
        assert pattern.search(entry).group(0) is not None
