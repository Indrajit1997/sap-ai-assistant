from __future__ import annotations

from backend.vectorstore.base import SearchResult

SAP_SYSTEM_PROMPT = """You are an expert SAP AI Assistant specializing in SAP technologies including S/4HANA, SuccessFactors, and integrations with Hyland platforms (OnBase, CIC, Alfresco).

Your role:
- Answer questions accurately based ONLY on the provided context documents
- Cite your sources with [Source N] references
- If the context doesn't contain enough information, say so clearly
- Use SAP-specific terminology correctly
- Provide actionable, implementation-focused answers
- When referencing SAP transactions, tables, or BAPIs, use their correct technical names

Important rules:
- NEVER make up information not present in the provided context
- If you're not confident in an answer, indicate your confidence level
- Always reference which source document(s) support your answer
- Format responses clearly with headers, bullet points, and code blocks where appropriate"""


def build_rag_prompt(query: str, results: list[SearchResult]) -> tuple[str, str]:
    """Build the prompt with retrieved context.

    Returns:
        (system_prompt, user_prompt) tuple
    """
    if not results:
        user_prompt = f"""Question: {query}

No relevant documents were found in the knowledge base for this question.
Please let the user know that you couldn't find specific documentation to answer their question,
and suggest they try rephrasing or check if the relevant documents have been ingested."""
        return SAP_SYSTEM_PROMPT, user_prompt

    # Build context block with source citations
    context_parts = []
    for i, result in enumerate(results, 1):
        source = result.metadata.get("source", "Unknown")
        page = result.metadata.get("page", "")
        module = result.metadata.get("sap_module", "")

        header = f"[Source {i}] {source}"
        if page:
            header += f" (Page {page})"
        if module:
            header += f" [{module}]"

        context_parts.append(f"{header}\n{result.content}")

    context_block = "\n\n---\n\n".join(context_parts)

    user_prompt = f"""Based on the following SAP documentation context, answer the question.
Always cite your sources using [Source N] notation.

CONTEXT:
{context_block}

---

Question: {query}

Provide a clear, actionable answer with source citations:"""

    return SAP_SYSTEM_PROMPT, user_prompt
