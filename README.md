# Base64 Regex

Regex for base64

## Usage

### Building a regex

To build a regex pattern for matching a specific string through base64, use the
`Segment.as_regex()` function:

```python
from b64_regex.recoder import Segment

segment = Segment(b"string-to-search")
segment.as_regex()

# Output:
# (?:c3RyaW5nLXRvLXNlYXJja[A-P]|[HXn3]N0cmluZy10by1zZWFyY2[g-j]|[BFJNRVZdhlptx159]zdHJpbmctdG8tc2VhcmNo)
```

Slightly more advanced patterns are supported via combination of segments with
normal regex. The `B64_CHARGROUP` variable contains `[a-zA-Z0-9\/\+]` for
convenience.

```python
from b64_regex.recoder import Segment, B64_CHARGROUP

start_segment = Segment(b"patternPrefix(")
end_segment = Segment(b")patternSuffix")

full_regex = f"{start_segment.as_regex()}{B64_CHARGROUP}+{end_segment.as_regex()}"

# Output:
# (?:cGF0dGVyblByZWZpeC[g-j]|[HXn3]BhdHRlcm5QcmVmaXgo|[BFJNRVZdhlptx159]wYXR0ZXJuUHJlZml4K[A-P])[a-zA-Z0-9\/\+]+(?:KXBhdHRlcm5TdWZmaX[g-j]|[CSiy]lwYXR0ZXJuU3VmZml4|[Acgkosw048]pcGF0dGVyblN1ZmZpe[A-P])
```

### Decoding matches

As around 33% of the matches are going to be misaligned by 6 or 12 bits,
decoding might need the prefixing of one or two b64 tokens to yield the right
results.

The `decode_all_alignments` function decodes the provided string with each bit
alignment and strips the prefixed extra data from the result. It however is not
able to know which result is correct, and instead returns all three:

```python
from b64_regex.recoder import decode_all_alignments

match = "cGF0dGVyblByZWZpeChmb28tYmFyLWNvbnRlbnQpcGF0dGVyblN1ZmZpeA=="
for x in decode_all_alignments(match):
    print(x)

# Output:
# b'patternPrefix(foo-bar-content)patternSuffix'
# b'\xc1\x85\xd1\xd1\x95\xc9\xb9A\xc9\x95\x99\xa5\xe0\xa1\x99\xbd\xbc\xb5\x89\x85\xc8\xb5\x8d\xbd\xb9\xd1\x95\xb9\xd0\xa5\xc1\x85\xd1\xd1\x95\xc9\xb9M\xd5\x99\x99\xa5\xe0'
# b'\x06\x17GFW&\xe5\x07&Vf\x97\x82\x86f\xf6\xf2\xd6&\x17"\xd66\xf6\xe7FV\xe7B\x97\x06\x17GFW&\xe57Vff\x97\x80'
# b'\x18]\x1d\x19\\\x9b\x94\x1c\x99Y\x9a^\n\x19\x9b\xdb\xcbX\x98\\\x8bX\xdb\xdb\x9d\x19[\x9d\n\\\x18]\x1d\x19\\\x9b\x94\xddY\x99\x9a^'
```

## Future work

It should be possible to translate some regex features to work within the b64
context (such as string length selectors / character repeats).
