import string

CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
CHARSET_REVERSE = {v: k for k, v in enumerate(CHARSET)}


def iter_windows(window_size: int, arr):
    for index in range(0, len(arr), window_size):
        yield arr[index : index + window_size]


def base64_encode(content: bytes) -> str:
    bits = "".join([f"{x:08b}" for x in content])

    if padding_bits := 6 - (len(bits) % 6):
        bits += padding_bits * "0"

    result = ""
    for window in iter_windows(6, bits):
        result += CHARSET[int(window, 2)]

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
