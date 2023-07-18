from bitarray import bitarray


def test_bits_str():
    ba = bitarray()
    ba.frombytes(b"Hello")
    encoded = ba.to01()
    ba = bitarray(encoded)
    assert ba.tobytes() == b"Hello"
