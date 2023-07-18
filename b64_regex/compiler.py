from base64 import b64encode
from typing import List


def make_alignment_variants(known: str) -> List[str]:
    if len(known) < 2:
        raise AttributeError("Search string must be at least 2 characters long")

    byted = known.encode()
    safe_tokens = (len(byted) * 8 // 6) - 1
    variant1 = b64encode(byted).decode()[:safe_tokens]
    variant2 = b64encode(f"aa{known}".encode()).decode()[3 : 3 + safe_tokens]
    variant3 = b64encode(f"a{known}".encode()).decode()[2 : 2 + safe_tokens]
    return [variant1, variant2, variant3]


def compile_regex_pattern(search_string: str):
    anchors = make_alignment_variants(search_string)
