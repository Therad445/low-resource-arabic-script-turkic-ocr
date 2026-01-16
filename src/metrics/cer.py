from __future__ import annotations

def _levenshtein(a: str, b: str) -> int:
    # Classic DP edit distance
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

def cer(ref: str, hyp: str) -> float:
    """
    Character Error Rate: edit_distance(ref, hyp) / len(ref)
    If ref is empty, returns 0 if hyp empty else 1.
    """
    ref = ref or ""
    hyp = hyp or ""
    if len(ref) == 0:
        return 0.0 if len(hyp) == 0 else 1.0
    return _levenshtein(ref, hyp) / float(len(ref))
