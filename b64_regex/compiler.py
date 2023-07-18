from base64 import b64encode
from typing import List

from b64_regex.recoder import (
    TokenSequence,
    bytes_to_bits,
    b64_encode_bits_without_padding,
)


class RegexSegment:
    def __init__(self, match_for: str):
        self.tokens = TokenSequence(bytes_to_bits(match_for.encode()))

    def as_regex(self) -> str:
        variants = [
            b64_encode_bits_without_padding(x)
            for x in self.tokens.with_all_alignments()
        ]
        return variants_to_regex(variants)


def variants_to_regex(variants: List[str]) -> str:
    return "|".join(variants).replace("/", "\\/").replace("+", "\\+")
