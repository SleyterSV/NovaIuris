# Sources and citations

Nova Iuris uses one provenance contract for public legal material and private case material. The backend definitions live in `app/services/source_contracts.py`; browser normalization is in `frontend/src/utils/sourceContract.js`.

## Source

A `Source` has a deterministic `source_id`, `source_scope` (`public` or `case`), a `source_type`, descriptive metadata, an exact `excerpt`, and available locators. Public identity derives from the repository record identity, locator and excerpt hash. Private identity derives from the tuple `case_id + document_id + chunk_id`. Array order is never used as identity.

Canonical shape (optional metadata stays `null` or is omitted by the renderer):

```json
{
  "source_id": "SRC-…",
  "source_scope": "public",
  "source_type": "jurisprudence",
  "title": "…",
  "entity": null,
  "court": "…",
  "case_number": "…",
  "article": null,
  "legal_basis": "…",
  "date": null,
  "document_id": "…",
  "case_id": null,
  "chunk_id": null,
  "page_start": null,
  "section": null,
  "excerpt": "Exact text excerpt",
  "official_url": null,
  "metadata": {}
}
```

Public records may include `official_url` only when that field is present on the record or its metadata and is an HTTP(S) URL. No URL is synthesized. A private source always requires `case_id`, `document_id` and `chunk_id`; its `official_url` is null. Page, section and paragraph appear only when the corpus supplies them.

## Citation and validation

A `Citation` identifies a `source_id`, has a stable `citation_id` and an answer-local visual label (`[1]`, `[2]`, ...). The label is not an identity. `CitationService.extract_citations()` returns `detected_legal_mentions`, which are regex mentions found in source text; these are not answer citations and do not prove that the source backs a model claim.

`ContextBuilder` returns `{text, sources}`. Each exact excerpt sent to the answer model is marked with `[SRC-…]`. `resolve_citations()` permits only markers that resolve to the sources in that context, deduplicates the source list, assigns answer-local labels and drops unrecognized markers with a warning. A private source is eligible only for an explicitly matching `case_id`. The resolver never searches globally for a private `source_id`.

Each emitted citation has `{citation_id, label, source_id, claim_id, excerpt, locator}`. Citation IDs remain stable for the same source excerpt; labels are assigned in first-use order for each generated answer.

NovaSearch returns `answer`, `documents`, `sources`, `citations`, `detected_legal_mentions`, `warnings` and `result_status`. A valid zero-result search is `no_results`; an unavailable legal repository raises `LegalSearchError` and the API responds with safe `SEARCH_FAILED`/503.

NovaCase carries corpus passages into canonical `sources`; the existing Case contract and NovaCourt pipeline preserve `sources` and `citations`. Claim-level citations for all internally generated NovaCase/NovaCourt sections are not yet emitted. No source attribution is fabricated for simulation roles or graph nodes.

## Frontend

`MarkdownRenderer` turns only labels backed by normalized citations into keyboard-operable buttons. Markdown HTML remains disabled and rendered text is escaped. `SourcesList` deduplicates by `source_id`; `SourceModal` hides missing fields and shows the exact excerpt. External links are shown only for normalized HTTP(S) `official_url` values with `noopener noreferrer`. Private entries show document ID and page/section when known. There is no authenticated document viewer in this block, so the modal does not link to local paths or fetch private content by an unscoped identifier.

## Limitations

- Search citations exist only when the model emits a valid supplied `[SRC-…]` marker.
- Existing citations in older Case/Court sections are preserved as-is; they are not retroactively verified.
- `official_url` quality depends on repository metadata being correct; this layer validates presence and scheme, not domain authority.
- A private document viewer and claim-level enrichment across every Case/Court section are future work.
