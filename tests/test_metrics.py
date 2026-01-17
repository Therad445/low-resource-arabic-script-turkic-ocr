from src.metrics.cer import cer
from src.metrics.wer import wer


def test_cer_basic():
    assert cer("abc", "abc") == 0.0
    assert cer("", "") == 0.0
    assert cer("", "a") == 1.0
    assert cer("a", "") == 1.0


def test_wer_basic():
    assert wer("hello world", "hello world") == 0.0
    assert wer("", "") == 0.0
    assert wer("", "hello") == 1.0
    assert wer("hello", "") == 1.0
