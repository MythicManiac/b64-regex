import string
import random
from typing import List, Iterable

FLAG_CHARACTERS = string.ascii_letters + string.digits


def get_random_string(length) -> str:
    return "".join(random.choice(FLAG_CHARACTERS) for _ in range(length))


def generate_flag(
    flag_prefix: str = "HTB",
    flag_wrapper_left: str = "{",
    flag_wrapper_right: str = "}",
    flag_length: int = 32,
) -> str:
    return f"{flag_prefix}{flag_wrapper_left}{get_random_string(flag_length)}{flag_wrapper_right}"


def generate_flags(flag_count: int = 32) -> List[str]:
    return [generate_flag() for _ in range(flag_count)]


def wrap_with_random_text(content: Iterable[str]) -> Iterable[str]:
    for entry in content:
        prefix = get_random_string(random.randint(0, 10))
        suffix = get_random_string(random.randint(0, 10))
        yield f"{prefix}{entry}{suffix}"
