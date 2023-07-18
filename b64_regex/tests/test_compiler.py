import csv
import pathlib
import re

from b64_regex.recoder import Segment, decode_all_alignments


def get_data_path(filename: str) -> pathlib.Path:
    return pathlib.Path(__file__).parent / "data" / filename


def test_find_matches():
    with open(get_data_path("test.txt"), "r") as f:
        lines = f.readlines()
    start_seq = Segment(b"HTB{")
    end_seq = Segment(b"}")

    pattern = re.compile(
        "(" f"{start_seq.as_regex()}" "[a-zA-Z0-9\\/\\+]+" f"{end_seq.as_regex()}" ")"
    )
    for entry in lines:
        assert pattern.search(entry).group(0) is not None


def test_find_and_decode_matches():
    with open(get_data_path("test.csv"), "r") as f:
        reader = csv.DictReader(f, fieldnames=["flag", "wrapped", "encoded"])
        lines = [x for x in reader][1:]

    start_seq = Segment(b"HTB{")
    end_seq = Segment(b"}")

    pattern = re.compile(
        "(" f"{start_seq.as_regex()}" "[a-zA-Z0-9\\/\\+]+" f"{end_seq.as_regex()}" ")"
    )
    for entry in lines:
        match = pattern.search(entry["encoded"]).group(0)
        assert match is not None
        assert entry["flag"].encode() in decode_all_alignments(match)
