from base64 import b64encode
from csv import DictWriter

from b64_regex.generate_test import generate_flags, wrap_with_random_text
from b64_regex.recoder import Segment, B64_CHARGROUP


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


def main():
    # dump_flags_to_txt("./test.txt")
    # dump_test_flags_to_file("./test.csv")

    start_seq = Segment(b"HTB{")
    end_seq = Segment(b"}")

    full_regex = (
        "(" f"{start_seq.as_regex()}" f"{B64_CHARGROUP}+" f"{end_seq.as_regex()}" ")"
    )
    print(full_regex)


if __name__ == "__main__":
    main()
