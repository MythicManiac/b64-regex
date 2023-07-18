import string
from typing import Literal, List, Tuple, Optional, Iterable

CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
CHARSET_REVERSE = {v: k for k, v in enumerate(CHARSET)}


Alignment = Literal[0, 2, 4]
ALL_ALIGNMENTS: Tuple[Literal[0], Literal[2], Literal[4]] = (0, 2, 4)


def stupid_pow(a: int, b: int) -> int:
    if b == 0:
        return 0
    return pow(a, b)


def as_regex_group(matches: List[str]) -> str:
    if not matches:
        return ""
    as_numbers = sorted(set((CHARSET_REVERSE[x] for x in matches)))

    matchgroups = []

    def add_matchgroup(start: int, end: int):
        if start != end:
            matchgroups.append(f"[{CHARSET[start]}-{CHARSET[end]}]")
        else:
            matchgroups.append(CHARSET[start])

    group_boundaries = (
        (CHARSET_REVERSE["a"], CHARSET_REVERSE["z"]),
        (CHARSET_REVERSE["A"], CHARSET_REVERSE["Z"]),
        (CHARSET_REVERSE["0"], CHARSET_REVERSE["9"]),
    )

    def is_in_group(val: int) -> Optional[Tuple[int, int]]:
        for (gmin, gmax) in group_boundaries:
            if gmin <= val <= gmax:
                return (gmin, gmax)
        return None

    class Cursor:
        current_group: Optional[Tuple[int, int]] = None
        start: Optional[int] = None
        end: Optional[int] = None

        def reset_cursor(self) -> Iterable[Tuple[int, int]]:
            if self.start and self.end:
                yield (self.start, self.end)
            self.start = None
            self.end = None
            self.current_group = None

        def record(self, current: int) -> Iterable[Tuple[int, int]]:
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

    cursor = Cursor()
    for entry in as_numbers:
        for x in cursor.record(entry):
            add_matchgroup(*x)
    for x in cursor.reset_cursor():
        add_matchgroup(*x)

    group = "|".join([x.replace("/", "\\/").replace("+", "\\+") for x in matchgroups])
    return f"(?:{group})"


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
            f"{as_regex_group(encode_multi(self.prefixes))}"
            f"{b64_encode_bits_without_padding(self.middle)}"
            f"{as_regex_group(encode_multi(self.suffixes))}"
        )


class SegmentVariantGroup:
    def __init__(self, segments: List[SegmentVariant]):
        self.segments = segments

    def as_regex(self) -> str:
        regexed = "|".join(x.as_regex() for x in self.segments)
        return f"(?:{regexed})"


class TokenSequence:
    bits: str

    def __init__(self, bits: str):
        self.bits = bits

    def with_alignment(self, alignment: Alignment) -> SegmentVariant:
        prefix_padding = alignment
        suffix_padding = 6 - ((len(self.bits) + alignment) % 6 or 6)
        variant_bits = prefix_padding + suffix_padding
        if variant_bits not in (0, 2, 4, 6):
            raise RuntimeError(f"Math doesn't check out: {variant_bits}")

        prefix_bits = (6 - prefix_padding) % 6
        prefix = self.bits[:prefix_bits] if prefix_bits else []

        suffix_bits = (6 - suffix_padding) % 6
        suffix = self.bits[-suffix_bits:] if suffix_bits else []

        middle = self.bits[prefix_bits : len(self.bits) - suffix_bits]

        assert len(prefix) + len(middle) + len(suffix) == len(self.bits)

        padded_prefixes = []
        for i in range(stupid_pow(2, prefix_padding)):
            padding_bits = f"{i:b}".zfill(prefix_padding)
            padded_prefixes.append(f"{padding_bits}{prefix}")

        padded_suffixes = []
        for i in range(stupid_pow(2, suffix_padding)):
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


def base64_decode(content: str) -> bytes:
    stripped = content.replace("=", "")
    token_bytes = [CHARSET_REVERSE[x] for x in stripped]
    bits = "".join(f"{x:06b}" for x in token_bytes)
    return bytes(int(x, 2) for x in iter_windows(8, bits) if len(x) == 8)
