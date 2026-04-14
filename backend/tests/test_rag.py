from backend.rag.prompt_builder import build_rag_prompt
from backend.vectorstore.base import SearchResult


def test_build_prompt_with_results():
    results = [
        SearchResult(
            id="1",
            content="SAP S/4HANA uses ACDOCA as the universal journal table.",
            score=0.92,
            metadata={"source": "s4hana_guide.pdf", "page": 42, "sap_module": "S4HANA"},
        ),
    ]
    system, user = build_rag_prompt("What is ACDOCA?", results)

    assert "SAP AI Assistant" in system
    assert "[Source 1]" in user
    assert "ACDOCA" in user
    assert "s4hana_guide.pdf" in user


def test_build_prompt_no_results():
    system, user = build_rag_prompt("What is BAPI?", [])
    assert "No relevant documents" in user


def test_build_prompt_multiple_sources():
    results = [
        SearchResult(id="1", content="Content A", score=0.9, metadata={"source": "a.pdf"}),
        SearchResult(id="2", content="Content B", score=0.8, metadata={"source": "b.pdf", "page": 5}),
    ]
    system, user = build_rag_prompt("test query", results)
    assert "[Source 1]" in user
    assert "[Source 2]" in user
    assert "a.pdf" in user
    assert "b.pdf" in user
