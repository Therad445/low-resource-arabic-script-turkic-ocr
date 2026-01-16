from __future__ import annotations

from .cer import _levenshtein

def wer(ref: str, hyp: str) -> float:
    """
    Word Error Rate: edit_distance(words(ref), words(hyp)) / len(words(ref))
    """
    ref_words = (ref or "").split()
    hyp_words = (hyp or "").split()
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    # Map word lists to a string of tokens via join with \u0001 separator
    # (or compute edit distance directly on lists by indexing)
    # Here we do list-based DP by converting to tuple and using _levenshtein on serialized tokens.
    # Simpler: join with a non-space separator and compute on tokens by replacing each word with a char is hard.
    # We'll do direct DP on lists below.
    return _levenshtein_list(ref_words, hyp_words) / float(len(ref_words))

def _levenshtein_list(a: list[str], b: list[str]) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]
