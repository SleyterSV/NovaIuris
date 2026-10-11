"""NovaSearch V2 runtime contract, with providers and database mocked."""

import re
import time
import unittest
from uuid import UUID
from unittest.mock import Mock, patch

from app.config import Config
from app.services.answer_service import AnswerService
from app.services.citation_service import CitationService
from app.services.context_builder import ContextBuilder
from app.services.legal_repository import LegalSearchError
from app.services.legal_repository_v2 import (LegalRepositoryV2, map_runtime_unit,
    search_cursor, UNIT_DETAIL_COLUMNS)
from app.services.legal_query_identity import explicit_tc_expediente, asks_for_decision
from app.services.search_service import SearchPipelineError, SearchService, word_safe_excerpt


def unit(unit_type="foundation", *, unit_id="unit-1", document_id="document-1",
         document_type="cassation", page=3, official_url=None):
    return {"unit_id": unit_id, "document_id": document_id,
            "document_title": "Casación 915-2022/ICA", "document_type": document_type,
            "unit_type": unit_type, "unit_number": "7", "heading": "Séptimo",
            "excerpt": "La lectura de la sentencia es un acto formal.",
            "page_start": page, "page_end": page, "similarity": 0.83,
            "lexical_score": 0.15, "official_url": official_url}


class RuntimeV2Tests(unittest.TestCase):
    def test_explicit_case_variants_decision_intent_and_ambiguity(self):
        variants = ("EXP. 04810-2024-PA/TC", "Expediente N.º 04810 - 2024 - pa / tc",
                    "EXPEDIENTE N° 4810–2024–PA/TC")
        for query in variants:
            self.assertEqual(explicit_tc_expediente(query), "04810-2024-PA/TC")
        self.assertEqual(explicit_tc_expediente("Exp. 00005-2025-PCC/TC"),
                         "00005-2025-PCC/TC")
        self.assertIsNone(explicit_tc_expediente("Casación 915-2022/ICA"))
        self.assertTrue(all(asks_for_decision(value) for value in
            ("¿Qué resolvió?", "¿Cuál fue la decisión?", "¿Cuál fue el fallo?", "¿Qué decidió?")))
        with self.assertRaises(ValueError):
            explicit_tc_expediente("04810-2024-PA/TC y 04826-2025-PHC/TC")

    def test_word_safe_preview_does_not_cut_words(self):
        preview = word_safe_excerpt("Primera oración completa. Segunda oración con más texto.", 38)
        self.assertEqual(preview, "Primera oración completa.…")
        preview = word_safe_excerpt("La decisión judicial requiere respaldo verificable.", 22)
        self.assertEqual(preview, "La decisión judicial…")
        self.assertEqual(word_safe_excerpt("Orientación al Ciudadano ( sin texto posterior", 28),
                         "Orientación al Ciudadano…")

    def test_rpc_arguments_filters_and_read_only_connection(self):
        row = tuple(unit().values())
        cursor = Mock()
        cursor.fetchall.side_effect = [[row], [("document-1", None, "915-2022/ICA", "915-2022/ICA",
                                               "Corte Suprema", "Sala Penal", None, None, None, None, "penal")]]
        connection = Mock(autocommit=False)
        connection.cursor.return_value = cursor
        repo = LegalRepositoryV2(connection_factory=lambda: connection)
        results = repo.search(embedding=[0.1] * 1536, query_text=" lectura ", match_count=7,
                              filter_document_type="cassation", filter_rama="penal",
                              filter_expediente="915-2022/ICA")
        self.assertEqual(results[0]["id"], "unit-1")
        self.assertEqual(results[0]["document_id"], "document-1")
        self.assertEqual(results[0]["page_start"], 3)
        self.assertEqual(cursor.execute.call_args_list[0].args[1][1:],
                         ("lectura", 7, "cassation", "penal", "915-2022/ICA"))
        self.assertIn("public.match_legal_knowledge_v2", cursor.execute.call_args_list[0].args[0])
        self.assertIn("public.legal_documents", cursor.execute.call_args_list[1].args[0])
        connection.set_session.assert_called_once_with(readonly=True)
        connection.rollback.assert_called_once()
        connection.close.assert_called_once()

    def test_empty_and_database_error_do_not_fall_back(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        connection = Mock(autocommit=False)
        connection.cursor.return_value = cursor
        repo = LegalRepositoryV2(connection_factory=lambda: connection)
        self.assertEqual(repo.search(embedding=[0.0] * 1536, query_text="consulta"), [])
        cursor.execute.side_effect = RuntimeError("private database detail")
        with self.assertRaises(LegalSearchError) as caught:
            repo.search(embedding=[0.0] * 1536, query_text="consulta")
        self.assertNotIn("private database detail", str(caught.exception))

    def test_repository_fails_closed_on_exact_case_metadata_mismatch(self):
        cursor = Mock()
        cursor.fetchall.side_effect = [
            [tuple(unit("decision", document_type="judgment").values())],
            [("document-1", None, None, "04826-2025-PHC/TC", "Tribunal Constitucional",
              None, None, None, None, None, None)],
        ]
        connection = Mock(autocommit=False)
        connection.cursor.return_value = cursor
        repo = LegalRepositoryV2(connection_factory=lambda: connection)
        with self.assertRaises(LegalSearchError):
            repo.search(embedding=[0.1] * 1536, query_text="04810-2024-PA/TC",
                        filter_expediente="04810-2024-PA/TC")
        connection.rollback.assert_called_once()

    def test_structured_metadata_builds_title_without_overwriting_editorial_title(self):
        row = unit("decision", document_type="judgment")
        row.update(expediente="04826-2025-PHC/TC", court="Tribunal Constitucional")
        mapped = map_runtime_unit(row)
        self.assertEqual(mapped["titulo"], "STC Exp. 04826-2025-PHC/TC")
        self.assertEqual(mapped["metadata"]["editorial_title"], row["document_title"])

    def test_cassation_and_decree_titles_use_verified_metadata(self):
        cassation = unit(document_type="cassation")
        cassation["document_title"] = "Título editorial incompleto..."
        cassation["expediente"] = "915-2022/ICA"
        self.assertEqual(map_runtime_unit(cassation)["titulo"], "Casación 915-2022/ICA")
        decree = unit(document_type="regulation")
        decree.update(number="006-2026-JUS", resolution_type="Decreto Supremo")
        self.assertEqual(map_runtime_unit(decree)["titulo"], "Decreto Supremo N.º 006-2026-JUS")

    def test_canonical_unit_detail_is_read_only_and_longer_than_rpc_preview(self):
        unit_id = "12345678-1234-1234-1234-123456789abc"
        document_id = "87654321-4321-4321-4321-cba987654321"
        canonical = "La decisión judicial requiere respaldo verificable. " * 20
        excerpt = canonical[:240]
        values = {"unit_id": unit_id, "document_id": document_id, "text": canonical,
                  "unit_type": "foundation", "unit_number": "Cuarto", "heading": "Cuarto",
                  "page_start": 5, "page_end": 6, "document_title": "Título editorial incompleto...",
                  "document_type": "cassation", "short_title": None, "number": None,
                  "expediente": "915-2022/ICA", "court": "Corte Suprema", "chamber": "Sala Penal",
                  "issuer": "Corte Suprema", "official_url": None, "resolution_type": "casación",
                  "materia": None, "sumilla": None}
        cursor = Mock()
        cursor.fetchone.return_value = tuple(values[column] for column in UNIT_DETAIL_COLUMNS)
        connection = Mock(autocommit=False)
        connection.cursor.return_value = cursor
        detail = LegalRepositoryV2(connection_factory=lambda: connection).get_unit(
            unit_id, document_id=document_id)
        self.assertEqual(detail["text"], canonical)
        self.assertGreater(len(detail["text"]), len(excerpt))
        self.assertEqual(detail["display_title"], "Casación 915-2022/ICA")
        self.assertIn("u.is_current", cursor.execute.call_args.args[0])
        self.assertIn("d.ingestion_status", cursor.execute.call_args.args[0])
        self.assertEqual(cursor.execute.call_args.args[1], (unit_id, document_id))
        self.assertIn("d.id = %s::uuid", cursor.execute.call_args.args[0])
        connection.set_session.assert_called_once_with(readonly=True)
        connection.rollback.assert_called_once()
        connection.close.assert_called_once()

    def test_unit_detail_missing_and_database_error(self):
        unit_id = "12345678-1234-1234-1234-123456789abc"
        cursor = Mock()
        cursor.fetchone.return_value = None
        connection = Mock(autocommit=False)
        connection.cursor.return_value = cursor
        repo = LegalRepositoryV2(connection_factory=lambda: connection)
        self.assertIsNone(repo.get_unit(unit_id))
        cursor.execute.side_effect = RuntimeError("private detail")
        with self.assertRaises(LegalSearchError) as caught:
            repo.get_unit(unit_id)
        self.assertNotIn("private detail", str(caught.exception))
        with self.assertRaises(ValueError):
            repo.get_unit("not-a-uuid")
        with self.assertRaises(ValueError):
            repo.get_unit(unit_id, document_id="not-a-uuid")

    def test_invalid_vector_and_result_shape(self):
        cursor = Mock()
        with self.assertRaises(ValueError):
            search_cursor(cursor, embedding=[0.1], query_text="consulta")
        cursor.execute.assert_not_called()
        cursor.fetchall.return_value = [(1, 2)]
        with self.assertRaises(ValueError):
            search_cursor(cursor, embedding=[0.1] * 1536, query_text="consulta")

    def test_unit_mapping_article_foundation_decision_cassation_and_missing_provenance(self):
        for kind in ("article", "foundation", "decision"):
            with self.subTest(kind=kind):
                row = unit(kind, page=None)
                mapped = map_runtime_unit(row)
                self.assertEqual(mapped["unit_type"], kind)
                self.assertEqual(mapped["id"], row["unit_id"])
                self.assertEqual(mapped["document_id"], row["document_id"])
                self.assertIsNone(mapped["page_start"])
                self.assertIsNone(mapped["official_url"])
                self.assertEqual(mapped["metadata"]["unit_type"], kind)
                self.assertEqual(mapped["articulo"], "Artículo 7" if kind == "article" else None)
                self.assertEqual(mapped["fundamento"], "Fundamento 7" if kind == "foundation" else None)
        self.assertEqual(map_runtime_unit(unit(document_type="regulation"))["source_type"], "legislation")

    @staticmethod
    def make_service(rows):
        service = SearchService.__new__(SearchService)
        service.knowledge_version = "v2"
        service.query_analyzer = Mock()
        service.query_analyzer.analyze.side_effect = lambda query: {"normalized_query": query}
        service.repository = Mock()
        service.repository.search.return_value = [map_runtime_unit(row) for row in rows]
        service.fusion_service = Mock()
        service.reranker = Mock()
        service.citation_service = CitationService()
        service.context_builder = ContextBuilder()
        service.answer_service = Mock()
        service.answer_service.generate_answer.side_effect = lambda query, context, **kwargs: {
            "answer": "Respuesta fundada " + re.search(r"\[SRC-[A-Za-z0-9_-]+\]", context).group(0)}
        service.answer_service.clean_answer.side_effect = AnswerService.clean_answer
        return service

    def test_context_answer_citations_preserve_unit_document_page_and_url(self):
        service = self.make_service([unit(), unit("decision", unit_id="unit-2", page=None,
                                                official_url="https://tc.gob.pe/decision")])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            result = service.search("¿Por qué la lectura es formal?", filtros={"modulo": "Todos"})
        self.assertEqual(result["metadata"]["knowledge_version"], "v2")
        self.assertEqual(result["documents"][0]["unit_id"], "unit-1")
        self.assertEqual(result["documents"][0]["document_id"], "document-1")
        self.assertEqual(result["sources"][0]["document_id"], "document-1")
        self.assertEqual(result["sources"][0]["chunk_id"], "unit-1")
        self.assertEqual(result["citations"][0]["locator"]["page"], 3)
        self.assertEqual(result["documents"][1]["official_url"], "https://tc.gob.pe/decision")
        self.assertIsNone(result["documents"][1]["page_start"])
        self.assertIn("[1]", result["answer"])
        self.assertEqual(result["documents"][0]["unit_type"], "foundation")
        self.assertIsNone(result["sources"][0]["article"])
        self.assertEqual(result["sources"][0]["legal_basis"], "Fundamento 7")
        self.assertEqual(result["documents"][1]["unit_type"], "decision")
        self.assertFalse(any(warning["code"] == "VIGENCIA_FILTER_UNAVAILABLE" for warning in result["warnings"]))
        service.fusion_service.fuse.assert_not_called()
        service.reranker.rerank.assert_not_called()
        service.repository.search.assert_called_once()

    def test_citation_without_page_or_official_url_invents_neither(self):
        service = self.make_service([unit("decision", page=None, official_url=None)])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            result = service.search("¿Qué resolvió el tribunal?")
        self.assertNotIn("page", result["citations"][0]["locator"])
        self.assertIsNone(result["sources"][0]["official_url"])
        self.assertIsNone(result["documents"][0]["page_start"])

    def test_v2_model_guard_and_filter(self):
        service = self.make_service([])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "wrong-model"
            with self.assertRaises(SearchPipelineError) as failed:
                service.search("consulta")
            self.assertEqual(failed.exception.code, "EMBEDDING_FAILED")
            service.repository.search.assert_not_called()
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            result = service.search("consulta", filtros={"modulo": "Civil"}, generate_answer=False)
        self.assertEqual(result["result_status"], "no_results")
        service.repository.search.assert_called_once_with(embedding=[0.1] * 1536,
            query_text="consulta", match_count=20, filter_rama="Derecho Civil", filter_expediente=None)

    def test_four_legal_question_contracts_with_mocked_v2_rows(self):
        scenarios = (
            ("¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444?",
             "regulation", "article", "TUO de la Ley 27444"),
            ("¿Cuál fue la decisión del TC en el expediente 04810-2024-PA/TC?",
             "order", "decision", "Auto Exp. 04810-2024-PA/TC"),
            ("¿Por qué la lectura de la sentencia es formal en la Casación 915-2022/ICA?",
             "cassation", "foundation", "Casación 915-2022/ICA"),
            ("¿Qué resolvió el TC en el expediente 04826-2025-PHC/TC?",
             "judgment", "decision", "STC Exp. 04826-2025-PHC/TC"),
        )
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            for index, (question, doc_type, unit_type, title) in enumerate(scenarios):
                with self.subTest(question=question):
                    row = unit(unit_type, unit_id=f"unit-{index}", document_id=f"doc-{index}",
                               document_type=doc_type, page=index + 1)
                    row["document_title"] = title
                    if index == 1:
                        row["expediente"] = "04810-2024-PA/TC"
                        row["excerpt"] = "RESUELVE Declarar IMPROCEDENTE el pedido de nulidad, entendido como aclaración."
                    if index == 3:
                        row["expediente"] = "04826-2025-PHC/TC"
                        row["court"] = "Tribunal Constitucional"
                        row["excerpt"] = "HA RESUELTO Declarar IMPROCEDENTE la demanda."
                    service = self.make_service([row])
                    result = service.search(question)
                    self.assertEqual(result["result_status"], "completed")
                    self.assertEqual(result["documents"][0]["titulo"], title)
                    self.assertEqual(result["documents"][0]["unit_type"], unit_type)
                    self.assertEqual(result["sources"][0]["document_id"], f"doc-{index}")
                    self.assertEqual(result["citations"][0]["locator"]["page"], index + 1)
                    self.assertIn(row["excerpt"], result["context"])
                    service.repository.search.assert_called_once_with(
                        embedding=[0.1] * 1536, query_text=question, match_count=20,
                        filter_rama=None, filter_expediente=row.get("expediente"))
                    if row.get("expediente"):
                        self.assertIn(row["excerpt"], result["answer"])
                        service.answer_service.generate_answer.assert_not_called()
                    if index == 3:
                        self.assertNotIn("vulneración de libertad", result["answer"].casefold())
                        self.assertEqual(result["documents"][0]["unit_type"], "decision")

    def test_exact_decision_prioritized_and_cross_document_context_excluded(self):
        wanted = "04810-2024-PA/TC"
        foreign = unit("decision", unit_id="foreign", document_id="other", document_type="judgment")
        foreign["expediente"] = "04826-2025-PHC/TC"
        foreign["excerpt"] = "HA RESUELTO Declarar IMPROCEDENTE la demanda."
        foundation = unit("foundation", unit_id="foundation", document_id="wanted", document_type="order")
        foundation["expediente"] = wanted
        decision = unit("decision", unit_id="decision", document_id="wanted", document_type="order")
        decision["expediente"] = wanted
        decision["excerpt"] = "RESUELVE Declarar IMPROCEDENTE el pedido de nulidad, entendido como aclaración."
        service = self.make_service([foreign, foundation, decision])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            result = service.search("¿Cuál fue la decisión del TC en el expediente 04810-2024-PA/TC?")
        self.assertEqual(result["documents"][0]["unit_id"], "decision")
        self.assertEqual(result["metadata"]["counts"]["retrieved_count"], 2)
        self.assertEqual(result["metadata"]["counts"]["used_source_count"], 1)
        self.assertEqual([source["document_id"] for source in result["sources"]], ["wanted"])
        self.assertIn(decision["excerpt"], result["answer"])
        self.assertNotIn(foreign["excerpt"], result["context"])
        self.assertNotIn(foundation["excerpt"], result["context"])
        service.answer_service.generate_answer.assert_not_called()
        self.assertFalse(any(warning["code"] == "NO_VERIFIABLE_SOURCES" for warning in result["warnings"]))

    def test_unknown_exact_case_never_semantically_substitutes(self):
        foreign = unit("decision", document_type="judgment")
        foreign["expediente"] = "04826-2025-PHC/TC"
        service = self.make_service([foreign])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            result = service.search("¿Qué resolvió en el expediente 99999-2025-PHC/TC?")
        self.assertEqual(result["result_status"], "no_exact_case_found")
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["warnings"][0]["code"], "NO_EXACT_CASE_FOUND")
        service.answer_service.generate_answer.assert_not_called()

    def test_exact_case_without_decision_does_not_infer_disposition(self):
        row = unit("foundation", document_type="judgment")
        row["expediente"] = "04826-2025-PHC/TC"
        service = self.make_service([row])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            result = service.search("¿Qué resolvió el TC en 04826-2025-PHC/TC?")
        self.assertEqual(result["result_status"], "no_exact_decision_found")
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["sources"], [])
        service.answer_service.generate_answer.assert_not_called()

    def test_vigencia_warning_only_for_explicit_request(self):
        row = unit("article", document_type="regulation")
        service = self.make_service([row])
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            ordinary = service.search("¿Dónde se publica el TUO de la Ley 27444?")
            asked = service.search("¿Sigue vigente el TUO de la Ley 27444?")
            explicit = service.search("¿Dónde se publica el TUO?",
                                      filtros={"solo_vigentes": True, "vigencia_explicit": True})
        for result in (asked, explicit):
            self.assertIn("VIGENCIA_FILTER_UNAVAILABLE", [warning["code"] for warning in result["warnings"]])
        self.assertNotIn("VIGENCIA_FILTER_UNAVAILABLE", [warning["code"] for warning in ordinary["warnings"]])

    def test_selector_uses_only_selected_repository(self):
        with patch("app.services.search_service.LegalRepository") as v1, \
             patch("app.services.search_service.LegalRepositoryV2") as v2, \
             patch("app.services.search_service.RerankerService"), \
             patch("app.services.search_service.AnswerService"):
            self.assertIs(SearchService().repository, v1.return_value)
            self.assertEqual(v2.call_count, 0)
            self.assertIs(SearchService(knowledge_version="v2").repository, v2.return_value)
            self.assertEqual(v1.call_count, 1)

    def test_endpoint_selector_does_not_change_case_search(self):
        from app import create_app
        from app.api.search import get_search_service
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            LEGAL_KNOWLEDGE_VERSION = "v2"
        app = create_app(TestConfig)
        with app.app_context(), patch("app.api.search.SearchService") as service:
            get_search_service()
            service.assert_called_once_with(knowledge_version="v2")
        with patch("app.services.search_service.LegalRepository") as v1, \
             patch("app.services.search_service.LegalRepositoryV2") as v2, \
             patch("app.services.search_service.RerankerService"), \
             patch("app.services.search_service.AnswerService"):
            SearchService()  # The constructor used by NovaCase remains V1.
            v1.assert_called_once()
            v2.assert_not_called()

    def test_v2_target_rejects_other_project_before_connection(self):
        with patch.dict("os.environ", {"MYKE_LEGAL_DATABASE_URL":
                "postgresql://postgres.other:secret@db.other.supabase.co:5432/postgres"}):
            with self.assertRaises(LegalSearchError):
                LegalRepositoryV2()

    def test_v2_ignores_fiscal_supabase_configuration(self):
        dsn = "postgresql://postgres.emelxkoztshmzukydqzj:secret@pooler.example:6543/postgres"
        with patch.dict("os.environ", {"MYKE_LEGAL_DATABASE_URL": dsn,
                                    "SUPABASE_URL": "https://fiscal-project.supabase.co",
                                    "SUPABASE_KEY": "fiscal-key"}), \
             patch("app.services.legal_repository_v2.postgres_connection_factory") as factory:
            LegalRepositoryV2()
        factory.assert_called_once_with(dsn)

    def test_api_sync_and_task_return_v2_contract(self):
        from app import create_app
        rows = [unit()]
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            LEGAL_KNOWLEDGE_VERSION = "v2"
            SEARCH_SERVICE_FACTORY = staticmethod(lambda: RuntimeV2Tests.make_service(rows))
        client = create_app(TestConfig).test_client()
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            response = client.post("/api/search", json={"query": "Casación 915-2022/ICA"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["documents"][0]["unit_id"], "unit-1")
            self.assertEqual(response.json["citations"][0]["locator"]["page"], 3)
            created = client.post("/api/search/tasks", json={"query": "Casación 915-2022/ICA"})
            self.assertEqual(created.status_code, 202)
            for _ in range(100):
                status = client.get("/api/search/tasks/" + created.json["task_id"])
                if status.json["status"] in {"completed", "failed"}:
                    break
                time.sleep(0.01)
        self.assertEqual(status.json["status"], "completed")
        self.assertEqual(status.json["final_result"]["metadata"]["knowledge_version"], "v2")
        self.assertEqual(status.json["final_result"]["sources"][0]["document_id"], "document-1")

    def test_api_v2_database_error_is_controlled_and_has_no_v1_fallback(self):
        from app import create_app
        def failed_service():
            service = RuntimeV2Tests.make_service([])
            service.repository.search.side_effect = LegalSearchError("private detail")
            return service
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            LEGAL_KNOWLEDGE_VERSION = "v2"
            SEARCH_SERVICE_FACTORY = staticmethod(failed_service)
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.1] * 1536
            response = create_app(TestConfig).test_client().post("/api/search", json={"query": "consulta"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["error"]["code"], "SEARCH_FAILED")
        self.assertNotIn("private detail", str(response.json))

    def test_source_detail_api_v2_only_and_one_unit(self):
        from app import create_app
        unit_id = "12345678-1234-1234-1234-123456789abc"
        document_id = "87654321-4321-4321-4321-cba987654321"
        class V2Config(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            LEGAL_KNOWLEDGE_VERSION = "v2"
        class V1Config(V2Config):
            LEGAL_KNOWLEDGE_VERSION = "v1"
        with patch("app.api.search.LegalRepositoryV2") as repository:
            repository.return_value.get_unit.return_value = {
                "unit_id": unit_id, "document_id": document_id,
                "text": "Texto completo de la unidad jurídica."}
            client = create_app(V2Config).test_client()
            response = client.get(f"/api/search/sources/{unit_id}?document_id={document_id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["unit"]["text"], "Texto completo de la unidad jurídica.")
            repository.return_value.get_unit.assert_called_once_with(
                UUID(unit_id), document_id=document_id)
            invalid = client.get(f"/api/search/sources/{unit_id}?document_id=bad")
            self.assertEqual(invalid.status_code, 400)
            self.assertEqual(client.get("/api/search/sources/not-a-uuid").status_code, 404)
            repository.return_value.get_unit.return_value = None
            self.assertEqual(client.get(f"/api/search/sources/{unit_id}?document_id={document_id}").status_code, 404)
            repository.return_value.get_unit.side_effect = LegalSearchError("private detail")
            failure = client.get(f"/api/search/sources/{unit_id}?document_id={document_id}")
            self.assertEqual(failure.status_code, 503)
            self.assertNotIn("private detail", str(failure.json))
            missing = create_app(V1Config).test_client().get(f"/api/search/sources/{unit_id}")
            self.assertEqual(missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()
