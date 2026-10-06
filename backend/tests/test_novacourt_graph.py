import unittest
from copy import deepcopy
from types import SimpleNamespace
from itertools import chain, repeat
from unittest.mock import patch
from app.utils.cancellation import CancellationToken, OperationCancelled
from app.services.graph_builder import GraphBuilderService, GraphProcessingTimeoutError as ProviderTimeout


from app.utils import novacourt_graph as NOVACOURT_GRAPH


def make_orchestrator(factory, enabled=True):
    return NOVACOURT_GRAPH.NovaCourtGraphOrchestrator(
        factory,
        enabled=enabled,
        timeout=12,
        poll_interval=2,
        chunk_size=500,
        chunk_overlap=50,
        batch_size=3,
    )


class ReadyBuilder:
    def __init__(self):
        self.request = None

    def create_graph(self, name):
        return 'zep-graph-1'
    def set_ontology(self, graph_id, ontology):
        pass
    def add_text_batches(self, graph_id, chunks, batch_size, cancellation_token=None):
        self.request = {'text': '\n'.join(chunks)}
        return [f'episode-{index}' for index in range(len(chunks))]
    def _wait_for_episodes(self, episodes, timeout=600, poll_interval=3, cancellation_token=None):
        self.request.update(timeout=timeout, poll_interval=poll_interval)
    def get_graph_data(self, graph_id, cancellation_token=None):
        return {'graph_id':graph_id, 'nodes':[{'uuid':'node-1','name':'Demandante'}],
                'edges':[{'uuid':'edge-1','source_node_uuid':'node-1','target_node_uuid':'node-1'}]}


class GraphProcessingTimeoutError(Exception):
    pass


class NovaCourtGraphTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "success": True,
            "case_id": "CASE-A",
            "summary": {"materia": "laboral"},
            "arguments": {"main_arguments": [{"text": "Reposición", "issue_id": "ISSUE-1",
                                                "supporting_fact_ids": ["FACT-1"]}]},
            "facts": [{"fact_id": "FACT-1", "text": "Despido", "status": "alleged"}],
            "issues": [{"issue_id": "ISSUE-1", "text": "Validez del despido"}],
            "internal_only": "no debe indexarse",
        }

    def test_canonical_contract_is_sent_to_builder_and_returns_ready_graph(self):
        builder = ReadyBuilder()
        result = make_orchestrator(lambda: builder).build(self.case)

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["graph_id"], "zep-graph-1")
        self.assertEqual(len(result["nodes"]), 4)
        self.assertGreaterEqual(len(result["edges"]), 4)
        self.assertIn("ARGUMENT", builder.request["text"])
        self.assertIn("FACT", builder.request["text"])
        self.assertNotIn("internal_only", builder.request["text"])
        self.assertGreater(builder.request["timeout"], 11)
        self.assertLessEqual(builder.request["timeout"], 12)
        self.assertEqual(builder.request["poll_interval"], 2)

    def test_builder_failure_preserves_case_analysis_and_has_safe_status(self):
        def failing_factory():
            raise RuntimeError("token secreto de Zep")

        result = make_orchestrator(failing_factory).build(self.case)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["is_final"], True)
        self.assertGreater(len(result["nodes"]), 0)
        self.assertNotIn("secreto", result["message"])
        self.assertEqual(self.case["arguments"]["main_arguments"][0]["text"], "Reposición")

    def test_timeout_has_distinct_safe_status(self):
        class TimeoutBuilder(ReadyBuilder):
            def _wait_for_episodes(self, episodes, timeout=600, poll_interval=3, cancellation_token=None):
                raise GraphProcessingTimeoutError("internal timeout detail")

        result = make_orchestrator(TimeoutBuilder).build(self.case)

        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["graph_id"], "zep-graph-1")
        self.assertNotIn("detail", result["message"])

    def test_disabled_graph_is_not_requested(self):
        result = make_orchestrator(ReadyBuilder, enabled=False).build(self.case)
        self.assertEqual(result["status"], "not_requested")
        self.assertEqual(result["nodes"], [])

    def rich_case(self):
        private = {"source_id": "SRC-PRIVATE-A", "source_scope": "case", "case_id": "CASE-A",
                   "source_type": "case_document", "title": "Contrato", "document_id": "DOC-A",
                   "chunk_id": "CHUNK-A", "page_start": 3, "section": "Segunda"}
        law = {"source_id": "SRC-LAW-A", "source_scope": "public", "source_type": "legislation",
               "title": "Ley laboral"}
        precedent = {"source_id": "SRC-JUR-A", "source_scope": "public", "source_type": "jurisprudence",
                     "title": "Sentencia", "court": "Corte", "case_number": "123",
                     "date": "2020-01-02", "official_url": "https://example.org/sentencia"}
        foreign = {**private, "case_id": "CASE-B", "source_id": "SRC-PRIVATE-B"}
        return {"case_id": "CASE-A", "summary": {"materia": "Laboral"},
                "analysis": {"partes": {"demandante": "Ana", "demandado": "Empresa"},
                             "pretension_principal": "Reposición",
                             "normas_probables": ["Norma preliminar"]},
                "sources": [private, law, precedent, foreign],
                "facts": [{"fact_id": f"F-{i}", "text": f"Hecho {i}", "status": status,
                           "source_ids": ["SRC-PRIVATE-A", "SRC-PRIVATE-B"]}
                          for i, status in enumerate(("alleged", "supported", "disputed", "unclear"))],
                "issues": [{"issue_id": "I-1", "text": "Validez del despido"}],
                "evidence": {"evidence_links": [{"text": "Contrato firmado", "fact_id": "F-1",
                    "issue_id": "I-1", "source_ids": ["SRC-PRIVATE-A", "SRC-PRIVATE-B"]}],
                    "recommended_evidence": ["Pericia futura"]},
                "arguments": {"main_arguments": [{"argument_id": "A-1", "text": "Reposición procede",
                    "issue_id": "I-1", "supporting_fact_ids": ["F-1"],
                    "source_ids": ["SRC-LAW-A", "SRC-JUR-A"]}]},
                "counter_arguments": {"main_counterarguments": [
                    {"text": "Empresa objeta", "argument_id": "A-1", "issue_id": "I-1"}]},
                "risks": {"critical_risks": [{"text": "Plazo", "issue_id": "I-1"}]},
                "timeline": [{"fact_id": "F-1", "date": "2024-01-01", "description": "Hecho 1"}]}

    def test_ontology_provenance_relations_and_isolation(self):
        graph = NOVACOURT_GRAPH.build_graph_input(self.rich_case())
        nodes, edges = graph["entities"], graph["relations"]
        types = {node["entity_type"] for node in nodes}
        self.assertTrue({"PARTY", "FACT", "EVIDENCE", "LEGAL_ISSUE", "LAW",
                         "JURISPRUDENCE", "ARGUMENT", "COUNTERARGUMENT", "RISK"} <= types)
        self.assertFalse(any("preliminar" in n["title"].lower() for n in nodes))
        self.assertFalse(any("Pericia futura" == n["title"] for n in nodes))
        self.assertFalse(any("SRC-PRIVATE-B" in n["source_ids"] for n in nodes))
        self.assertFalse(any("SRC-PRIVATE-B" in e["source_ids"] for e in edges))
        facts = {n["fact_id"]: n for n in nodes if n["entity_type"] == "FACT"}
        self.assertEqual([facts[f"F-{i}"]["status"] for i in range(4)],
                         ["alleged", "supported", "disputed", "unclear"])
        evidence = next(n for n in nodes if n["entity_type"] == "EVIDENCE")
        self.assertEqual((evidence["document_id"], evidence["chunk_id"], evidence["page_start"]),
                         ("DOC-A", "CHUNK-A", 3))
        precedent = next(n for n in nodes if n["entity_type"] == "JURISPRUDENCE")
        self.assertEqual(precedent["case_number"], "123")
        self.assertEqual(precedent["official_url"], "https://example.org/sentencia")
        identifiers = {node["node_id"] for node in nodes}
        self.assertTrue(all(e["source_node_id"] in identifiers and e["target_node_id"] in identifiers
                            for e in edges))
        self.assertTrue(all(e["relation_type"] in NOVACOURT_GRAPH.RELATION_TYPES for e in edges))
        self.assertTrue({"PROVES", "CITES", "COUNTERS", "CREATES_RISK"} <=
                        {e["relation_type"] for e in edges})
        self.assertFalse(any(e["relation_type"] == "RELATED_TO" for e in edges))

    def test_stable_identity_and_conservative_deduplication(self):
        case = self.rich_case()
        case["analysis"]["partes"].update({"tribunal": "Tribunal Constitucional",
                                            "juez": "El Tribunal Constitucional.",
                                            "fiscal": "Tribunal Constitucional Norte"})
        first = NOVACOURT_GRAPH.build_graph_input(case)
        reversed_case = deepcopy(case)
        reversed_case["facts"].reverse()
        reversed_case["sources"].reverse()
        second = NOVACOURT_GRAPH.build_graph_input(reversed_case)
        self.assertEqual({n["node_id"] for n in first["entities"]},
                         {n["node_id"] for n in second["entities"]})
        parties = [n for n in first["entities"] if n["entity_type"] == "PARTY"]
        self.assertEqual(len(parties), 4)  # Ana, Empresa, tribunal, similarly named northern tribunal

    def test_ontology_aliases_and_relation_pairs(self):
        aliases = {"Parte": "PARTY", "Hecho": "FACT", "Pretensión": "CLAIM",
                   "Pretension": "CLAIM", "Norma": "LAW", "Argumento": "ARGUMENT",
                   "Evidencia": "EVIDENCE", "Riesgo": "RISK",
                   "Actuación": "PROCEDURAL_ACT", "Actuacion": "PROCEDURAL_ACT"}
        for name, expected in aliases.items():
            self.assertEqual(NOVACOURT_GRAPH.normalize_entity_type(name), expected)
        self.assertIsNone(NOVACOURT_GRAPH.normalize_entity_type("parece una norma"))
        self.assertEqual(set(NOVACOURT_GRAPH.RELATION_TYPES),
                         {entry["name"] for entry in NOVACOURT_GRAPH.LEGAL_ONTOLOGY["edge_types"]})
        graph = NOVACOURT_GRAPH.build_graph_input(self.rich_case())
        by_id = {node["node_id"]: node["entity_type"] for node in graph["entities"]}
        for edge in graph["relations"]:
            pair = (by_id[edge["source_node_id"]], by_id[edge["target_node_id"]])
            self.assertIn(pair, NOVACOURT_GRAPH._RELATION_PAIRS[edge["relation_type"]])
        self.assertNotIn(("LAW", "FACT"), NOVACOURT_GRAPH._RELATION_PAIRS["PROVES"])

    def test_identity_provenance_and_missing_endpoints(self):
        case = self.rich_case()
        graph = NOVACOURT_GRAPH.build_graph_input(case)
        other = deepcopy(case)
        other["case_id"] = "CASE-B"
        other["sources"] = [source for source in other["sources"]
                            if source["source_scope"] == "public"]
        second = NOVACOURT_GRAPH.build_graph_input(other)
        self.assertFalse({n["node_id"] for n in graph["entities"]} &
                         {n["node_id"] for n in second["entities"]})
        self.assertFalse({e["edge_id"] for e in graph["relations"]} &
                         {e["edge_id"] for e in second["relations"]})
        self.assertEqual(len({e["edge_id"] for e in graph["relations"]}), len(graph["relations"]))
        evidence = next(n for n in graph["entities"] if n["entity_type"] == "EVIDENCE")
        self.assertEqual(evidence["source_ids"], ["SRC-PRIVATE-A"])
        proof = next(e for e in graph["relations"] if e["relation_type"] == "PROVES")
        self.assertEqual(proof["source_ids"], ["SRC-PRIVATE-A"])
        self.assertEqual(proof["metadata"]["chunk_id"], "CHUNK-A")
        self.assertTrue(all(n["entity_type"] and n["metadata"]["origin"]
                            for n in graph["entities"]))
        case["evidence"]["evidence_links"].append({"text": "Sin hecho existente",
            "fact_id": "MISSING", "source_ids": ["SRC-PRIVATE-A"]})
        updated = NOVACOURT_GRAPH.build_graph_input(case)
        self.assertFalse(any(edge["target_node_id"] == "MISSING" for edge in updated["relations"]))

    def test_grounded_metadata_and_no_invented_authority(self):
        case = self.rich_case()
        case["risks"]["critical_risks"][0]["probability"] = 0.8
        case["timeline"].append({"act_id": "ACT-1", "text": "Audiencia", "date": "2024-02-01"})
        graph = NOVACOURT_GRAPH.build_graph_input(case)
        types = {node["entity_type"] for node in graph["entities"]}
        self.assertIn("PROCEDURAL_ACT", types)
        self.assertNotIn("probability", next(n for n in graph["entities"] if n["entity_type"] == "RISK"))
        argument = next(n for n in graph["entities"] if n["entity_type"] == "ARGUMENT")
        self.assertEqual(argument["fact_ids"], ["F-1"])
        self.assertEqual(argument["issue_id"], "I-1")
        self.assertTrue(any(e["relation_type"] == "COUNTERS" for e in graph["relations"]))
        self.assertFalse(any(n["title"] == "Norma preliminar" for n in graph["entities"]))

    def test_global_remaining_deadline_and_partial_failure_version(self):
        case = self.rich_case()
        builder = ReadyBuilder()
        ticks = chain([0], repeat(4))
        with patch.object(NOVACOURT_GRAPH, "time", SimpleNamespace(monotonic=lambda: next(ticks))):
            result = make_orchestrator(lambda: builder).build(case)
        self.assertEqual(builder.request["timeout"], 8)
        self.assertEqual(result["status"], "ready")
        partials = []
        failed = make_orchestrator(lambda: (_ for _ in ()).throw(RuntimeError("private"))).build(
            case, snapshot_callback=partials.append)
        self.assertEqual((partials[0]["version"], failed["version"]), (1, 2))
        self.assertTrue(failed["is_final"])
        self.assertEqual(failed["nodes"], partials[0]["nodes"])
        self.assertTrue(failed["warnings"])

    def test_provider_polling_obeys_one_deadline_without_long_sleep(self):
        builder = object.__new__(GraphBuilderService)
        calls = []
        def get_episode(uuid_):
            calls.append(uuid_)
            return SimpleNamespace(processed=False)
        builder.client = SimpleNamespace(graph=SimpleNamespace(
            episode=SimpleNamespace(get=get_episode)))
        ticks = iter(i * .25 for i in range(30))
        fake_time = SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None)
        with patch("app.services.graph_builder.time", fake_time):
            with self.assertRaises(ProviderTimeout):
                builder._wait_for_episodes(["episode-1"], timeout=1, poll_interval=2)
        self.assertGreaterEqual(len(calls), 1)
        self.assertLessEqual(len(calls), 4)

    def test_real_snapshots_and_deadline(self):
        builder = ReadyBuilder()
        snapshots = []
        result = make_orchestrator(lambda: builder).build(
            self.rich_case(), snapshot_callback=snapshots.append)
        self.assertEqual([s["version"] for s in snapshots] + [result["version"]], [1, 2])
        self.assertFalse(snapshots[0]["is_final"])
        self.assertTrue(result["is_final"])
        self.assertEqual(result["metadata"]["snapshot_count"], 2)
        self.assertEqual(result["metadata"]["batch_count"],
                         (len(result["nodes"]) + len(result["edges"]) + 2) // 3)

    def test_cancellation_stops_new_work(self):
        token = CancellationToken()
        class CancelBuilder(ReadyBuilder):
            def add_text_batches(self, graph_id, chunks, batch_size, cancellation_token=None):
                token.cancel()
                return ["episode-1"]
            def _wait_for_episodes(self, *args, **kwargs):
                self.fail("poll must not start")
        builder = CancelBuilder()
        with self.assertRaises(OperationCancelled):
            make_orchestrator(lambda: builder).build(self.rich_case(), cancellation_token=token)


if __name__ == "__main__":
    unittest.main()
