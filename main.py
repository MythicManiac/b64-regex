from b64_regex.generate_test import generate_flags, wrap_with_random_text


def main():
    flags = generate_flags()
    for flag, wrapped in zip(flags, wrap_with_random_text(flags)):
        print(f"{flag=} | {wrapped=}")


if __name__ == "__main__":
    main()
