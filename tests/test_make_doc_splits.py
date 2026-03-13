from scripts.make_doc_splits import assign_docs_balanced
from src.data.manifest import DocumentStats


def test_assign_docs_balanced_keeps_all_docs_and_is_deterministic():
    stats = [
        DocumentStats(doc_id="d1", source_id="s1", n_pages=1, n_lines=10),
        DocumentStats(doc_id="d2", source_id="s1", n_pages=1, n_lines=9),
        DocumentStats(doc_id="d3", source_id="s2", n_pages=1, n_lines=8),
        DocumentStats(doc_id="d4", source_id="s2", n_pages=1, n_lines=7),
    ]
    left = assign_docs_balanced(doc_stats=stats, seed=42)
    right = assign_docs_balanced(doc_stats=stats, seed=42)

    assert left == right
    assert set(left) == {"d1", "d2", "d3", "d4"}
    assert set(left.values()).issubset({"train", "dev", "test"})


def test_assign_docs_balanced_handles_two_docs_safely():
    stats = [
        DocumentStats(doc_id="d1", source_id="s1", n_pages=1, n_lines=10),
        DocumentStats(doc_id="d2", source_id="s2", n_pages=1, n_lines=8),
    ]
    assignments = assign_docs_balanced(doc_stats=stats, seed=42)

    assert assignments["d1"] == "train"
    assert assignments["d2"] == "test"
