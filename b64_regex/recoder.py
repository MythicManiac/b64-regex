from bitarray import bitarray

import string

CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
CHARSET_REVERSE = {v: k for k, v in enumerate(CHARSET)}


def iter_windows(window_size: int, arr):
    for index in range(0, len(arr), window_size):
        yield arr[index : index + window_size]


def base64_encode(content: bytes) -> str:
    ba = bitarray()
    ba.frombytes(content)

    if padding_bits := 6 - (len(ba) % 6):
        ba.extend(padding_bits * "0")

    result = ""
    for window in iter_windows(6, ba):
        window = bitarray(f"00{window.to01()}")
        result += CHARSET[int.from_bytes(window.tobytes())]

    if padding_chars := 4 - (len(result) % 4):
        result += "=" * padding_chars

    return result


def base64_decode(content: str) -> bytes:
    stripped = content.replace("=", "")
    token_bytes = [CHARSET_REVERSE[x] for x in stripped]
    bits = "".join(f"{x:06b}" for x in token_bytes)
    return bytes(int(x, 2) for x in iter_windows(8, bits) if len(x) == 8)


class Recoder:
    def __init__(self):
        pass
