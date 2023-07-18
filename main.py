from base64 import b64encode
from csv import DictWriter
from typing import List

from b64_regex.compiler import make_alignment_variants
from b64_regex.generate_test import generate_flags, wrap_with_random_text
from b64_regex.recoder import (
    base64_encode,
    base64_decode,
    TokenSequence,
    bytes_to_bits,
    b64_encode_bits_without_padding,
)


def dump_test_flags_to_csv(destination: str):
    with open(destination, "w", newline="") as f:
        writer = DictWriter(f, fieldnames=["flag", "wrapped", "encoded"])
        flags = generate_flags(1000)
        writer.writeheader()
        for flag, wrapped in zip(flags, wrap_with_random_text(flags)):
            encoded = b64encode(wrapped.encode()).decode()
            writer.writerow(
                {
                    "flag": flag,
                    "wrapped": wrapped,
                    "encoded": encoded,
                }
            )


def dump_flags_to_txt(destination: str):
    with open(destination, "w") as f:
        flags = generate_flags(1000)
        lines = [
            b64encode(x.encode()).decode() + "\n" for x in wrap_with_random_text(flags)
        ]
        f.writelines(lines)


def print_test_flags():
    flags = generate_flags()
    for flag, wrapped in zip(flags, wrap_with_random_text(flags)):
        encoded = b64encode(wrapped.encode())
        print(f"{flag=} | {wrapped=} | {encoded=}")


def build_regex():
    print(make_alignment_variants("HTB{"))


def variants_to_regex(variants: List[str]) -> str:
    return "|".join(variants).replace("/", "\\/").replace("+", "\\+")


def main():
    # dump_flags_to_txt("./test.txt")
    # dump_test_flags_to_file("./test.csv")
    # build_regex()
    # from base64 import b64encode
    #
    # print(b64encode(b"Hello"))
    # encoded = base64_encode(b"Hello")
    # print(encoded)
    # print(base64_decode(encoded))

    # seq = TokenSequence(bytes_to_bits(b"Three days grade school,"))
    # vars = [b64_encode_bits_without_padding(x) for x in seq.with_all_alignments()]
    # regx = variants_to_regex(vars)
    # print(regx)

    start_seq = TokenSequence(bytes_to_bits(b"HTB{"))
    start_variants = [
        b64_encode_bits_without_padding(x) for x in start_seq.with_all_alignments()
    ]
    start_regex = variants_to_regex(start_variants)

    end_seq = TokenSequence(bytes_to_bits(b"}"))
    end_variants = [
        b64_encode_bits_without_padding(x) for x in end_seq.with_all_alignments()
    ]
    end_regex = variants_to_regex(end_variants)

    full_regex = f"({start_regex})" "[a-zA-Z0-9\\/\\+]+" f"({end_regex})"

    print(full_regex)


if __name__ == "__main__":
    main()
