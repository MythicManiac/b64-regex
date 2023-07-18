from base64 import b64encode
from typing import List

from bitarray import bitarray


def make_alignment_variants(known: str) -> List[str]:
    if len(known) < 3:
        raise AttributeError("Search string must be at least 3 characters long")

    byted = known.encode()
    variant1 = b64encode(byted).decode().replace("=", "")
    variant2 = b64encode(f"aa{known}".encode()).decode().replace("=", "")[3:-1]
    variant3 = b64encode(f"a{known}".encode()).decode().replace("=", "")[2:-1]
    return [variant1, variant2, variant3]


def compile_regex_pattern(search_string: str):
    anchors = make_alignment_variants(search_string)
