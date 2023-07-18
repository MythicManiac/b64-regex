import string
from typing import Literal, Iterable

CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
CHARSET_REVERSE = {v: k for k, v in enumerate(CHARSET)}


Alignment = Literal[0, 2, 4]


def stupid_pow(a: int, b: int) -> int:
    if b == 0:
        return 0
    return pow(a, b)


class TokenSequence:
    bits: str

    def __init__(self, bits: str):
        self.bits = bits

    def with_alignment(self, alignment: Alignment) -> Iterable[str]:
        prefix_bits = alignment
        suffix_bits = 6 - ((len(self.bits) + alignment) % 6 or 6)
        variant_bits = prefix_bits + suffix_bits
        if variant_bits not in (0, 2, 4, 6):
            raise RuntimeError(f"Math doesn't check out: {variant_bits}")

        if variant_bits == 0:
            yield self.bits

        for i in range(stupid_pow(2, variant_bits)):
            padding_bits = f"{i:b}".zfill(variant_bits)
            prefix = padding_bits[:prefix_bits]
            suffix = padding_bits[prefix_bits:]
            yield f"{prefix}{self.bits}{suffix}"

    def with_all_alignments(self) -> Iterable[str]:
        for alignment in (0, 2, 4):
            for entry in self.with_alignment(alignment):
                yield entry


def iter_windows(window_size: int, arr):
    for index in range(0, len(arr), window_size):
        yield arr[index : index + window_size]


def bytes_to_bits(content: bytes) -> str:
    return "".join([f"{x:08b}" for x in content])


def base64_encode(content: bytes) -> str:
    encoded = b64_encode_bits_without_padding(bytes_to_bits(content))
    return add_b64_padding(encoded)


def b64_encode_bits_without_padding(bits: str) -> str:
    if padding_bits := 6 - ((len(bits) % 6) or 6):
        bits += padding_bits * "0"

    result = ""
    for window in iter_windows(6, bits):
        result += CHARSET[int(window, 2)]

    return result


def add_b64_padding(encoded: str) -> str:
    if padding_chars := 4 - ((len(encoded) % 4) or 4):
        encoded += "=" * padding_chars
    return encoded


def base64_decode(content: str) -> bytes:
    stripped = content.replace("=", "")
    token_bytes = [CHARSET_REVERSE[x] for x in stripped]
    bits = "".join(f"{x:06b}" for x in token_bytes)
    return bytes(int(x, 2) for x in iter_windows(8, bits) if len(x) == 8)
