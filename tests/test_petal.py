"""
unit tests for sp5n.petal
"""

import pytest

from sp5n.petal import Bloom, Word


def test_word_from_bloom():
    bloom_input: Bloom = Bloom(("-",) * 11 + ("*", "2"))
    word = Word(bloom_input)
    expected_int = (1 << 5) | 2
    assert word.as_int == expected_int
    assert word.as_bloom == bloom_input


def test_word_from_int():
    int_input = 12345
    word = Word(int_input)
    expected_bloom: Bloom = Bloom(("-",) * 10 + ("G", "*", "t"))
    assert word.as_bloom == expected_bloom
    assert word.as_int == int_input


def test_word_from_large_int():
    # largest positive value in a 64-bit signed integer
    # 0x7FFFFFFFFFFFFFFF = 13 groups of 5 bits: 0b00111 then twelve 0b11111
    large_int = (2**63) - 1
    word = Word(large_int)
    assert word.as_int == large_int
    expected_bloom: Bloom = Bloom(
        (
            "8",  #  7 - 0b00111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
        )
    )
    assert word.as_bloom == expected_bloom


def test_word_from_small_int():
    # largest negative value in a 64-bit signed integer
    # 0x8000000000000000 = 13 groups of 5 bits: 0b01000 then twelve 0b00000
    small_int = -(2**63)
    word = Word(small_int)
    assert word.as_int == small_int
    expected_bloom: Bloom = Bloom(
        (
            "c",  # 8 - 0b01000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
            "-",  # 0 - 0b00000
        )
    )
    assert word.as_bloom == expected_bloom


def test_word_from_negative_one():
    # -1 = 0xFFFFFFFFFFFFFFFF = 13 groups of 5 bits: 0b01111 then twelve 0b11111
    word = Word(-1)
    assert word.as_int == -1
    expected_bloom: Bloom = Bloom(
        (
            "j",  # 15 - 0b01111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
            "#",  # 31 - 0b11111
        )
    )
    assert word.as_bloom == expected_bloom


def test_word_invalid_int():
    with pytest.raises(
        ValueError,
        match="value '9223372036854775808' wont fit in a 64 bit signed integer",
    ):
        Word(2**63)


def test_word_invalid_bloom():
    invalid_bloom: Bloom = Bloom(("k",) + ("-",) * 12)
    with pytest.raises(
        ValueError, match="cant create word from a bloom with more than 64 bits"
    ):
        Word(invalid_bloom)
