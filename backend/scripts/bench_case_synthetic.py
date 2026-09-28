"""Local synthetic NovaCase benchmark. Uses only the existing test fakes."""
import json
from time import perf_counter, sleep
from unittest.mock import Mock, patch

from tests.test_stabilization import case_service


SCENARIOS = {
    "small": {"queries": ["consulta civil"], "characters": 300, "documents": 0},
    "medium": {"queries": ["consulta civil", " consulta   civil ", "CONSULTA CIVIL", "otra cuestión"],
               "characters": 3000, "documents": 0},
    "large_document": {"queries": ["consulta civil", " consulta   civil ", "CONSULTA CIVIL", "otra cuestión"],
                       "characters": 12000, "documents": 8},
}


def run_scenario(name, delay_seconds=0.002):
    fixture = SCENARIOS[name]
    service = case_service()
    service.strategy_builder.build_strategy.return_value = {
        "search_queries": fixture["queries"], "claim_strategy": "Evaluar hechos y fuentes"}
    document_ids = [f"DOC-{index}" for index in range(fixture["documents"])]
    chunks = [{"text": "Fragmento jurídico " * 40, "document_id": document_id,
               "chunk_id": f"CH-{index}",
               "source_reference": {"case_id": "CASE-SYNTHETIC", "document_id": document_id,
                                    "chunk_id": f"CH-{index}", "page_start": index + 1}}
              for index, document_id in enumerate(document_ids)]
    service.case_corpus_repository = Mock()
    service.case_corpus_repository.list_documents.return_value = [
        {"document_id": document_id, "filename": f"doc-{index}.pdf"}
        for index, document_id in enumerate(document_ids)]
    for field, method in (("case_analyzer", "analyze_case"), ("strategy_builder", "build_strategy"),
                          ("search_service", "search"), ("argument_service", "generate_arguments"),
                          ("evidence_analyzer", "analyze"), ("risk_analyzer", "analyze"),
                          ("counter_argument_service", "generate_counterarguments"),
                          ("report_service", "generate_report")):
        mock = getattr(getattr(service, field), method)
        original = mock.return_value
        def delayed(*args, _value=original, _field=field, **kwargs):
            sleep(delay_seconds)
            if _field == "search_service" and kwargs.get("progress_callback"):
                kwargs["progress_callback"]("embedding", "running")
                kwargs["progress_callback"]("retrieval", "running")
            return _value
        mock.side_effect = delayed
    def fake_context(*args, **kwargs):
        callback = kwargs.get("operation_callback")
        if callback:
            callback("embedding")
            callback("retrieval")
        return chunks
    started = perf_counter()
    with patch("app.services.embedding_service.EmbeddingService", return_value=Mock()), \
         patch("app.services.case_corpus.CaseContextService.relevant_context", side_effect=fake_context) as corpus:
        result = service.analyze_case("Caso ficticio. " * (fixture["characters"] // 16),
                                      case_id="CASE-SYNTHETIC", document_ids=document_ids)
    elapsed_ms = round((perf_counter() - started) * 1000, 2)
    stages = ["case_analyzer", "strategy_builder", "argument_service", "evidence_analyzer",
              "risk_analyzer", "counter_argument_service", "report_service"]
    calls = {field: getattr(getattr(service, field), {
        "case_analyzer": "analyze_case", "strategy_builder": "build_strategy",
        "argument_service": "generate_arguments", "evidence_analyzer": "analyze",
        "risk_analyzer": "analyze", "counter_argument_service": "generate_counterarguments",
        "report_service": "generate_report"}[field]).call_count for field in stages}
    document_chars = sum(len(json.dumps(call.kwargs.get("documents", []), ensure_ascii=False, default=str))
                         for field, method in (("argument_service", "generate_arguments"),
                                               ("evidence_analyzer", "analyze"), ("risk_analyzer", "analyze"),
                                               ("counter_argument_service", "generate_counterarguments"))
                         for call in getattr(getattr(service, field), method).call_args_list)
    return {"scenario": name, "synthetic_wall_ms": elapsed_ms,
            "llm_service_calls": sum(calls.values()),
            "research_calls": service.search_service.search.call_count,
            "private_context_calls": corpus.call_count,
            "embedding_operations": result["metadata"]["counts"]["embedding_call_count"],
            "retrieval_operations": result["metadata"]["counts"]["retrieval_call_count"],
            "document_input_chars": document_chars,
            "result_keys": sorted(result.keys())}


if __name__ == "__main__":
    for scenario in SCENARIOS:
        print(json.dumps(run_scenario(scenario), ensure_ascii=False))
