import string
from typing import Literal, List, Tuple, Optional, Iterable

CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
CHARSET_REVERSE = {v: k for k, v in enumerate(CHARSET)}


Alignment = Literal[0, 2, 4]
ALL_ALIGNMENTS: Tuple[Literal[0], Literal[2], Literal[4]] = (0, 2, 4)
REGEX_GROUP_BOUNDARIES = (
    (CHARSET_REVERSE["a"], CHARSET_REVERSE["z"]),
    (CHARSET_REVERSE["A"], CHARSET_REVERSE["Z"]),
    (CHARSET_REVERSE["0"], CHARSET_REVERSE["9"]),
)

B64_CHARGROUP = "[a-zA-Z0-9\\/\\+]"


def is_in_group(val: int) -> Optional[Tuple[int, int]]:
    for (gmin, gmax) in REGEX_GROUP_BOUNDARIES:
        if gmin <= val <= gmax:
            return (gmin, gmax)
    return None


class GroupBuilder:
    current_group: Optional[Tuple[int, int]] = None
    start: Optional[int] = None
    end: Optional[int] = None

    def reset_cursor(self) -> Iterable[Tuple[int, int]]:
        if self.start is not None and self.end is not None:
            yield (self.start, self.end)
        self.start = None
        self.end = None
        self.current_group = None

    def add(self, current: int) -> Iterable[Tuple[int, int]]:
        group = is_in_group(current)
        if group != self.current_group or (self.end and current > self.end + 1):
            for x in self.reset_cursor():
                yield x

        if group is None:
            yield [current, current]
        else:
            if self.current_group is None:
                self.current_group = group
                self.start = current
                self.end = current
            elif current == (self.end + 1):
                self.end = current


def pow_or_zero(a: int, b: int) -> int:
    if b == 0:
        return 0
    return pow(a, b)


def escape_chargroup(chargroup: str) -> str:
    return chargroup.replace("/", "\\/").replace("+", "\\+")


def as_regex_chargroup(characters: List[str]) -> str:
    if not characters:
        return ""

    as_numbers = sorted(set((CHARSET_REVERSE[x] for x in characters)))
    chargroups = []

    def add_matchgroup(start: int, end: int):
        if start != end:
            if end - start > 2:
                chargroups.append(f"{CHARSET[start]}-{CHARSET[end]}")
            else:
                chargroups.append(CHARSET[start])
                chargroups.append(CHARSET[end])
        else:
            chargroups.append(CHARSET[start])

    builder = GroupBuilder()
    for entry in as_numbers:
        for x in builder.add(entry):
            add_matchgroup(*x)
    for x in builder.reset_cursor():
        add_matchgroup(*x)

    group = "".join([escape_chargroup(x) for x in chargroups])
    if len(chargroups) == 0:
        raise RuntimeError("This shouldn't happen")
    return f"[{group}]"


def encode_multi(entries: List[str]) -> List[str]:
    return [b64_encode_bits_without_padding(x) for x in entries]


class SegmentVariant:
    prefixes: List[str]
    middle: str
    suffixes: List[str]

    def __init__(self, prefixes: List[str], middle: str, suffixes: List[str]):
        self.prefixes = prefixes
        self.middle = middle
        self.suffixes = suffixes

    def as_regex(self) -> str:
        return (
            f"{as_regex_chargroup(encode_multi(self.prefixes))}"
            f"{b64_encode_bits_without_padding(self.middle)}"
            f"{as_regex_chargroup(encode_multi(self.suffixes))}"
        )


class SegmentVariantGroup:
    def __init__(self, segments: List[SegmentVariant]):
        self.segments = segments

    def as_regex(self) -> str:
        regexed = "|".join(x.as_regex() for x in self.segments)
        return f"(?:{regexed})"


class Segment:
    bits: str

    def __init__(self, plaintext_bytes: bytes):
        self.bits = bytes_to_bits(plaintext_bytes)

    def with_alignment(self, alignment: Alignment) -> SegmentVariant:
        prefix_padding = alignment
        suffix_padding = 6 - ((len(self.bits) + alignment) % 6 or 6)
        if prefix_padding not in (0, 2, 4) or suffix_padding not in (0, 2, 4):
            raise RuntimeError(
                f"Math doesn't check out: {prefix_padding=}, {suffix_padding=}"
            )

        prefix_bits = (6 - prefix_padding) % 6
        prefix = self.bits[:prefix_bits] if prefix_bits else []

        suffix_bits = (6 - suffix_padding) % 6
        suffix = self.bits[-suffix_bits:] if suffix_bits else []

        middle = self.bits[prefix_bits : len(self.bits) - suffix_bits]

        assert len(prefix) + len(middle) + len(suffix) == len(self.bits)

        padded_prefixes = []
        for i in range(pow_or_zero(2, prefix_padding)):
            padding_bits = f"{i:b}".zfill(prefix_padding)
            padded_prefixes.append(f"{padding_bits}{prefix}")

        padded_suffixes = []
        for i in range(pow_or_zero(2, suffix_padding)):
            padding_bits = f"{i:b}".zfill(suffix_padding)
            padded_suffixes.append(f"{suffix}{padding_bits}")

        return SegmentVariant(padded_prefixes, middle, padded_suffixes)

    def with_all_alignments(self) -> SegmentVariantGroup:
        return SegmentVariantGroup([self.with_alignment(x) for x in ALL_ALIGNMENTS])

    def as_regex(self) -> str:
        return self.with_all_alignments().as_regex()


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


def bits_to_bytes(bits: str) -> bytes:
    return bytes(int(x, 2) for x in iter_windows(8, bits) if len(x) == 8)


def base64_decode(content: str) -> bytes:
    stripped = content.replace("=", "")
    token_bytes = [CHARSET_REVERSE[x] for x in stripped]
    bits = "".join(f"{x:06b}" for x in token_bytes)
    return bits_to_bytes(bits)


def decode_all_alignments(encoded: str) -> List[bytes]:
    stripped = encoded.replace("=", "")
    token_bytes = [CHARSET_REVERSE[x] for x in stripped]
    bits = "".join(f"{x:06b}" for x in token_bytes)
    result = []
    for prefix_bits in (0, 6, 12, 18):
        prefix = "0" * prefix_bits
        decoded = bits_to_bytes(f"{prefix}{bits}")[prefix_bits // 6 :]
        result.append(decoded)
    return result
