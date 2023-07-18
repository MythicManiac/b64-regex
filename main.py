from base64 import b64encode
from csv import DictWriter

from b64_regex.compiler import make_alignment_variants
from b64_regex.generate_test import generate_flags, wrap_with_random_text
from b64_regex.recoder import base64_encode, base64_decode


def dump_test_flags_to_file(destination: str):
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


def print_test_flags():
    flags = generate_flags()
    for flag, wrapped in zip(flags, wrap_with_random_text(flags)):
        encoded = b64encode(wrapped.encode())
        print(f"{flag=} | {wrapped=} | {encoded=}")


def build_regex():
    print(make_alignment_variants("HTB{"))


def main():
    # dump_test_flags_to_file("./test.csv")
    # build_regex()
    from base64 import b64encode

    print(b64encode(b"Hello"))
    encoded = base64_encode(b"Hello")
    print(encoded)
    print(base64_decode(encoded))


if __name__ == "__main__":
    main()
